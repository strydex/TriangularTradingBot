import datetime
import json
import math
from decimal import Context, setcontext, Decimal, ROUND_UP, ROUND_DOWN
from binance import Client
import client_creator
import config
from binance_parser.config import redis


def precision_and_scale(x):
    max_digits = 14
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
    if magnitude >= max_digits:
        return (magnitude, 0)
    frac_part = abs(x) - int_part
    multiplier = 10 ** (max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    scale = int(math.log10(frac_digits))
    return (magnitude + scale, scale)


def send_deal(pair_name, target_side, order_quantity, buy_price):
    order = client_creator.client.create_order(
        symbol=pair_name,
        side=target_side,
        type=Client.ORDER_TYPE_LIMIT,
        timeInForce=Client.TIME_IN_FORCE_IOC,
        quantity=order_quantity,
        price=float(buy_price))
    return order


def get_pair_trade_data(pair_name):
    raw_pair_trade_data = redis.get(f"coin-data_{pair_name}")
    if raw_pair_trade_data is not None:
        pair_trade_data = json.loads(raw_pair_trade_data)
    else:
        raise TypeError(f'NO REDIS DATA FOR {pair_name}')
    return pair_trade_data


def trade(deal_data):
    print(deal_data)

    if deal_data[0]['bundle']['base'] + deal_data[0]['bundle']['target'] == deal_data[0]['bundle']['pair_name']:

        target_side = Client.SIDE_SELL
        order_quantity = config.USDT_ORDER_SIZE
    else:
        target_side = Client.SIDE_BUY
        pair_trade_data = get_pair_trade_data(deal_data[0]['bundle']['pair_name'])
        max_qty_precision = precision_and_scale(float(pair_trade_data['stepSizeQty']))

        order_quantity = round(config.USDT_ORDER_SIZE * 1 / deal_data[0]['price']['based_low_price'], max_qty_precision[1])

    print('order_quantity', order_quantity)
    order = send_deal(deal_data[0]['bundle']['pair_name'], target_side, order_quantity, deal_data[0]['price']['based_low_price'])
    print(order)
    coins_qty = float(order['executedQty'])


    for fills in order['fills']:
        if fills['commissionAsset'] == deal_data[0]['bundle']['target']:
            coins_qty -= float(fills['commission'])

    print('after comission 0 coins_qty', coins_qty)


    pair_trade_data = get_pair_trade_data(deal_data[1]['bundle']['pair_name'])
    max_qty_precision = precision_and_scale(float(pair_trade_data['stepSizeQty']))


    if deal_data[1]['bundle']['base'] + deal_data[1]['bundle']['target'] == deal_data[1]['bundle']['pair_name']:
        target_side = Client.SIDE_SELL
        order_quantity = math.floor(coins_qty * 10 ** max_qty_precision[1]) / 10 ** max_qty_precision[1]
    else:
        target_side = Client.SIDE_BUY

        raw_order_quantity = coins_qty * 1 / deal_data[1]['price']['based_low_price']

        order_quantity = math.floor(raw_order_quantity * 10 ** max_qty_precision[1]) / 10 ** max_qty_precision[1]

    print('1 order_quantity', order_quantity)
    print('price for order 1', deal_data[1]['price']['based_low_price'])
    order = send_deal(deal_data[1]['bundle']['pair_name'], target_side, order_quantity,
                      deal_data[1]['price']['based_low_price'])



    print(order)
    coins_qty = float(order['cummulativeQuoteQty'])

    for fills in order['fills']:
        if fills['commissionAsset'] == deal_data[1]['bundle']['target']:
            coins_qty -= float(fills['commission'])

    print('after comission 1 coins_qty', coins_qty)



    if deal_data[2]['bundle']['base'] + deal_data[2]['bundle']['target'] == deal_data[2]['bundle']['pair_name']:
        target_side = Client.SIDE_SELL

        # raw_order_quantity = coins_qty * 1 / deal_data[2]['price']['based_low_price']
        # order_quantity = math.floor(raw_order_quantity * 1 ** max_qty_precision[1]) / 1 ** max_qty_precision[1]
        order_quantity = math.floor(coins_qty * 10 ** max_qty_precision[1]) / 10 ** max_qty_precision[1]


    else:
        target_side = Client.SIDE_BUY
        raw_order_quantity = coins_qty * 1 / deal_data[2]['price']['based_low_price']
        print('raw_order_quantity 2', raw_order_quantity)
        print('deal_data[2] price', deal_data[2]['price']['based_low_price'])
        print('max_qty_precision[1]', max_qty_precision[1])

        order_quantity = math.floor(raw_order_quantity * 10 ** max_qty_precision[1]) / 10 ** max_qty_precision[1]


    print('2 order_quantity', order_quantity)
    print('price for order 2', deal_data[2]['price']['based_low_price'])
    order = send_deal(deal_data[2]['bundle']['pair_name'], target_side, order_quantity,
                      deal_data[2]['price']['based_low_price'])

    print(order)
