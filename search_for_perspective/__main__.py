import json
import random
import time

import requests

from binance_parser.config import redis


def unpack_coins_data():
    pairs_dict = dict()
    data = requests.get('https://api1.binance.com/api/v3/exchangeInfo')
    if data.status_code == 200:
        for coin in data.json()['symbols']:
            if coin['status'] == 'TRADING' and coin['isSpotTradingAllowed']:
                if coin['baseAsset'] not in pairs_dict.keys():
                    pairs_dict[coin['baseAsset']] = [coin['quoteAsset']]
                else:
                    pairs_dict[coin['baseAsset']].append(coin['quoteAsset'])
                if coin['quoteAsset'] not in pairs_dict.keys():
                    pairs_dict[coin['quoteAsset']] = [coin['baseAsset']]
                else:
                    pairs_dict[coin['quoteAsset']].append(coin['baseAsset'])

        result = ({0: {'base': currency, 'target': variants},
                   1: {'base': variants, 'target': second_variants},
                   2: {'base': second_variants, 'target': currency}}
                  for currency in pairs_dict.keys() for variants in pairs_dict[currency]
                  for second_variants in pairs_dict[variants]
                  if variants in pairs_dict[currency] and second_variants != currency and currency != 'AXS' and second_variants != 'AXS')
        return result
    else:
        raise ConnectionError


def get_price_data():
    price_data_dict = {}
    for keys in redis.keys('price-data_*'):
        price_data_dict[keys.split('_')[1]] = json.loads(redis.get(keys))
    return price_data_dict


def pair_data_unpack(pair_data):
    try:
        pair_price_data = price_data_dict.get(f"{pair_data['base']}{pair_data['target']}")
        if pair_price_data is None:
            pair_price_data = price_data_dict.get(f"{pair_data['target']}{pair_data['base']}")
            if pair_price_data is not None:
                price = {'price': 1 / float(pair_price_data['a']), 'volume': pair_price_data['A'],
                         'pair_name': f"{pair_data['target']}{pair_data['base']}"}
                return price
        if pair_price_data is not None:
            price = {'price': pair_price_data['b'], 'volume': pair_price_data['B'],
                     'pair_name': f"{pair_data['base']}{pair_data['target']}"}
            return price
        return None
    except TypeError as e:
        print(e)


if __name__ == '__main__':

    while True:

        try:
            start_time = round(time.time())
            bundles_list = unpack_coins_data()
            price_data_dict = get_price_data()

            for pairs in bundles_list:


                first = pair_data_unpack(pairs[0])
                second = pair_data_unpack(pairs[1])
                third = pair_data_unpack(pairs[2])

                if first is not None and second is not None and third is not None:
                    pairs[0]['pair_name'] = first['pair_name']
                    pairs[1]['pair_name'] = second['pair_name']
                    pairs[2]['pair_name'] = third['pair_name']

                    profit = ((10 * float(first['price'])) * float(second['price'])) * float(third['price'])

                    if profit > 10.03:
                        # print(pairs)
                        # print(first)
                        # print(second)
                        # print(third)
                        # print(profit)

                        # print('Opportunity is found!\n'
                        #       f'{pairs[0]["base"]} > {pairs[0]["target"]} {pairs[1]["base"]} > {pairs[1]["target"]} {pairs[2]["base"]} > {pairs[2]["target"]}\n'
                        #       f'{pairs[0]["base"]} > {pairs[0]["target"]} {first}\n'
                        #       f'{pairs[1]["base"]} > {pairs[1]["target"]} {second}\n'
                        #       f'{pairs[2]["base"]} > {pairs[2]["target"]} {third}\n'
                        #       f'Enter - 10, Exit: {profit}')



                        redis.set(f"target-to-check_{random.randint(0, 99999)}", json.dumps({'bundle': pairs}), 2)

            print(time.time() - start_time)
        except:
            pass
