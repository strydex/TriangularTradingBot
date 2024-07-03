import json
import random
import threading
import time
import os
import requests
import binance_deal
from binance_parser.config import redis, TELEGRAM_CHAT_ID

usdt_minimal_value = 100


def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


last_token = 0

# Replace these tokens below with your actual bot tokens acquired via Botfather in Telegram
bot_tokens_list = ['TOKEN_1',
                   'TOKEN_2',
                   'TOKEN_3',
                   'TOKEN_4',
                   'TOKEN_5',
                   'TOKEN_6',
                   'TOKEN_7',
                   'TOKEN_8']


def get_fresh_token():
    global last_token
    try:
        token = bot_tokens_list[last_token]
        last_token += 1
    except IndexError:
        token = bot_tokens_list[0]
        last_token = 0
    return token


def send_to_telegram(message):
    response = requests.get(
        f'https://api.telegram.org/bot{get_fresh_token()}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}&parse_mode=HTML')


def get_depth(pair_name):
    resp = requests.get(f'https://api1.binance.com/api/v3/depth?symbol={pair_name}')
    if resp.status_code == 200:
        redis.set(f'depth-data_{pair_name}', json.dumps(resp.json()), 50)
    else:
        send_to_telegram('Query limit exceeded!')
        raise ConnectionError(resp.status_code)


# def get_bundle_data():
#     target_bundle_dict = {}
#     for keys in redis.keys('target-to-check_*'):
#         try:
#             target_bundle_dict[keys.split('_')[1]] = json.loads(redis.get(keys))
#         except TypeError:
#             pass
#     return target_bundle_dict


def get_currency_bundle():
    target_bundle_dict = dict()
    for keys in redis.keys('target-to-check_*'):
        try:
            target_bundle_dict[keys.split('_')[1]] = json.loads(redis.get(keys))
        except TypeError:
            pass
    sorted_bundles_dict_by_currency = dict()
    good_currency_list = ['USDT']

    for pair_id, pair_data in target_bundle_dict.items():

        for pairs_id in ['0', '1', '2']:
            if pairs_id == '0':
                second_pair_id = '2'
                third_pair_id = '1'
            elif pairs_id == '1':
                second_pair_id = '0'
                third_pair_id = '2'
            else:
                second_pair_id = '1'
                third_pair_id = '0'

            if pair_data['bundle'][pairs_id]['base'] in good_currency_list and pair_data['bundle'][second_pair_id][
                'target'] in good_currency_list:
                sorted_bundles_dict_by_currency[pairs_id] = {'bundle':
                                                                 {'0': pair_data['bundle'][pairs_id],
                                                                  '1': pair_data['bundle'][third_pair_id],
                                                                  '2': pair_data['bundle'][second_pair_id]}}
        return sorted_bundles_dict_by_currency


def get_usdt_price(base):
    if base == 'USDT':
        return 1
    price_to_ustd = redis.get(f'price-data_{base}USDT')
    if price_to_ustd is None:
        price_to_ustd = redis.get(f'price-data_USDT{base}')
        price_to_ustd_json = json.loads(price_to_ustd)
        return (float(price_to_ustd_json['b']) + float(price_to_ustd_json['a'])) / 2
    price_to_ustd_json = json.loads(price_to_ustd)
    return (float(price_to_ustd_json['b']) + float(price_to_ustd_json['a'])) / 2


# def deep_unpack(pair_price_data, user_base_token_price, pair_data):
#     deep = 0
#     depth_volume = float(pair_price_data['asks'][0][1])
#     while depth_volume * user_base_token_price < 100:
#         try:
#             deep += 1
#             depth_volume += float(pair_price_data['asks'][deep][1])
#         except IndexError:
#             return None
#
#     price = {'price': 1 / float(pair_price_data['asks'][deep][0]), 'volume': depth_volume * user_base_token_price,
#              'pair_name': f"{pair_data['target']}{pair_data['base']}"}
#     return price


def pair_data_unpack(pair_data):
    try:
        if pair_data['base'] != 'USDT':
            user_base_token_price = get_usdt_price(pair_data['base'])
        else:
            user_base_token_price = get_usdt_price(pair_data['target'])


        pair_price_data = depth_data.get(f"{pair_data['base']}{pair_data['target']}")
        if pair_price_data is None:
            pair_price_data = depth_data.get(f"{pair_data['target']}{pair_data['base']}")

            if pair_price_data is not None:
                deep = 0
                depth_volume = float(pair_price_data['asks'][0][1])
                while depth_volume * user_base_token_price < usdt_minimal_value:
                    try:
                        deep += 1
                        depth_volume += float(pair_price_data['asks'][deep][1])
                    except IndexError:
                        return None

                price = {'price': 1 / float(pair_price_data['asks'][deep][0]),
                         'low_price': 1 / float(pair_price_data['asks'][0][0]),
                         'based_price': float(pair_price_data['asks'][deep][0]),
                         'based_low_price': float(pair_price_data['asks'][0][0]),
                         'volume': depth_volume * user_base_token_price,
                         'coin_volume': depth_volume,
                         'pair_name': f"{pair_data['target']}{pair_data['base']}"}
                return price
        if pair_price_data is not None:
            deep = 0
            depth_volume = float(pair_price_data['bids'][0][1])
            while depth_volume * user_base_token_price < usdt_minimal_value:
                try:
                    deep += 1
                    depth_volume += float(pair_price_data['bids'][deep][1])
                except IndexError:
                    return None

            price = {'price': float(pair_price_data['bids'][deep][0]),
                     'volume': depth_volume * user_base_token_price,
                     'low_price': float(pair_price_data['bids'][0][0]),
                     'based_price': float(pair_price_data['bids'][deep][0]),
                     'based_low_price': float(pair_price_data['bids'][0][0]),
                     'coin_volume': depth_volume,
                     'pair_name': f"{pair_data['base']}{pair_data['target']}"}
            return price
        return None
    except TypeError as e:
        print(e)


def get_depth_data():
    depth_data_dict = {}
    for keys in redis.keys('depth-data_*'):
        try:
            depth_data_dict[keys.split('_')[1]] = json.loads(redis.get(keys))
        except TypeError:
            pass
    return depth_data_dict


while True:
    depth_data = get_depth_data()
    current_bundle_dict = get_currency_bundle()
    start_time = time.time()

    try:
        pairs_list = set(bundle_data['pair_name'] for _, bundles in current_bundle_dict.items() for _, bundle_data in
                         bundles['bundle'].items())
    except AttributeError:
        print('skip')
    else:

        threads_list = [threading.Thread(target=get_depth, args=(pair,)) for pair in pairs_list]
        for threads in threads_list:
            threads.start()
        for threads in threads_list:
            threads.join()

        for _, pairs in current_bundle_dict.items():
            pairs = pairs['bundle']

            first = pair_data_unpack(pairs['0'])
            second = pair_data_unpack(pairs['1'])
            third = pair_data_unpack(pairs['2'])

            if first is not None and second is not None and third is not None:

                profit = ((10 * float(first['price'])) * float(second['price'])) * float(third['price'])
                top_profit = ((10 * float(first['low_price'])) * float(second['low_price'])) * float(third['low_price'])

                print(profit)

                if 9.9 < profit < 20:

                    try:
                        binance_deal.trade({0: {'bundle': pairs['0'],
                                                'price': first,
                                                'volume': first['volume']},
                                            1: {'bundle': pairs['1'],
                                                'price': second,
                                                'volume': second['volume']},
                                            2: {'bundle': pairs['2'],
                                                'price': third,
                                                'volume': third['volume']}})
                    except Exception as e:
                        print(e)

                    thread = threading.Thread(target=send_to_telegram,
                                              args=(
                                                  f"<a href='https://www.binance.com/ru/trade/{first['pair_name']}'>{pairs['0']['base']} > {pairs['0']['target']}</a>: {first['price']} // {1 / first['price']}\n\n"
                                                  f"<a href='https://www.binance.com/ru/trade/{second['pair_name']}'>{pairs['1']['base']} > {pairs['1']['target']}</a>: {second['price']} // {1 / second['price']}\n\n"
                                                  f"<a href='https://www.binance.com/ru/trade/{third['pair_name']}'>{pairs['2']['base']} > {pairs['2']['target']}</a>: {third['price']} // {1 / third['price']}\n\n"
                                                  f"<b>Profit</b>: {round(get_change(10, profit), 3)}%+\n"
                                                  f"Top profit: {round(get_change(10, top_profit), 3)}%\n"
                                                  f"Max <b>Volume: {min([third['volume'], second['volume'], first['volume']])} USDT</b>",))
                    thread.start()

    print(f'done {random.randint(0, 1)}')


