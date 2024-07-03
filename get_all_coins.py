import json

import requests
from binance_parser.config import redis

def get_coins():
    data = requests.get('https://api1.binance.com/api/v1/exchangeInfo')
    if data.status_code == 200:
        json_data = data.json()
        for symbols in json_data['symbols']:
            redis.set(f'coin-data_{symbols["symbol"]}', json.dumps({"baseAsset": symbols['baseAsset'],
                           "quoteAsset": symbols['quoteAsset'],
                           "minPrice": symbols['filters'][0]['minPrice'],
                           "maxPrice": symbols['filters'][0]['maxPrice'],
                           "maxQty": symbols['filters'][2]['maxQty'],
                           "minQty": symbols['filters'][2]['minQty'],
                           "tickSizePrice": symbols['filters'][0]['tickSize'],
                           "stepSizeQty": symbols['filters'][2]['stepSize'],
                           "min_national": symbols['filters'][3]['minNotional']}))

    else:
        raise ConnectionError(f'binance connection error {data.status_code}')

