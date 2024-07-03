import json
import websocket
from binance_parser.config import redis

socket = f"wss://stream.binance.com:9443/ws/!bookTicker"


def on_message(ws, message):
    json_message = json.loads(message)
    redis.set(f'price-data_{json_message["s"]}', json.dumps({'b': json_message['b'],
                                             'a': json_message['a'],
                                             'B': json_message['B'],
                                             'A': json_message['A']}))


def on_close(ws):
    print('closed')


def on_error(ws, message):
    raise ConnectionError(str(message))


ws = websocket.WebSocketApp(socket, on_message=on_message, on_close=on_close, on_error=on_error)
