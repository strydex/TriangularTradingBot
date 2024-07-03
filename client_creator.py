from binance import Client
import config
import time

client = Client(config.binance_api_key, config.binance_secret_key)
