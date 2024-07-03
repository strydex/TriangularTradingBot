import json
import requests


def get_data():
    names_dict = {}
    data = requests.get('https://api1.binance.com/api/v1/exchangeInfo')
    if data.status_code == 200:
        for symbols in data.json()['symbols']:
            names_dict[symbols['symbol']] = {'baseAsset' : symbols['baseAsset'] , "quoteAsset": symbols['quoteAsset']}
        return names_dict
    raise ConnectionError('cant connect binance to get pairs!')

