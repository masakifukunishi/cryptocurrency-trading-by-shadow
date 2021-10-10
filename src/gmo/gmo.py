from datetime import datetime, timedelta
from decimal import Decimal
import dateutil.parser
import math
import time
import requests
import json
import pytz
import hmac
import hashlib
import websocket
import logging

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)

class Margin(object):
    def __init__(self, available):
        self.available = int(available)    

class Order(object):
    def __init__(self, product_code, side, size, price='',
                 execution_type='LIMIT', time_in_force='FAK', status=None, order_id=None):
        self.product_code = product_code
        self.side = side
        self.size = size
        self.price = price
        self.execution_type = execution_type
        self.time_in_force = time_in_force
        self.status = status
        self.order_id = order_id

class OrderTimeoutError(Exception):
    """Order timeout error"""

class APIClient(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.product_code = settings.product_code
        self.public_end_point = settings.gmo_public_end_point
        self.private_end_point = settings.gmo_private_end_point
        # path
        self.send_order_path = settings.gmo_send_order_path
        self.send_bulk_close_order_path = settings.gmo_send_bulk_close_order_path
        self.send_cancel_bulk_order_path = settings.gmo_send_cancel_bulk_order_path
        self.send_cancel_order_path = settings.gmo_send_cancel_order_path
        self.send_cancel_orders_path = settings.gmo_send_cancel_orders_path
        self.get_orderbooks_path = settings.gmo_get_orderbooks_path
        self.get_order_path = settings.gmo_get_order_path

    def get_orderbooks(self):
        try:
            method = 'GET'
            end_point = self.public_end_point
            path = self.get_orderbooks_path.format(product_code=self.product_code)
            headers = self.make_headers(method, path)
            resp = requests.get(end_point + path, headers=headers)
        except Exception as e:
            logger.error(f'action=get_orderbooks error={e}')
            raise
        bids = resp.json()['data']['bids'][0:100]
        asks = resp.json()['data']['asks'][0:100]
        return bids, asks

    def send_order(self, order: Order):
        method = 'POST'
        end_point = self.private_end_point
        path = self.send_order_path

        request_body = {
            'symbol': order.product_code,
            'side': order.side,
            'executionType': order.execution_type,
            'size': order.size,
            'price': order.price,
            'time_in_force': order.time_in_force
        }

        headers = self.make_headers(method, path, request_body)
        try:
            resp = requests.post(end_point + path, headers=headers, data=json.dumps(request_body))
        except Exception as e:
            logger.error(f'action=send_order error={e}')
            raise
        
        order_id = resp.json()['data']        
        return order_id

    def get_order(self, order_id):
        method = 'GET'
        end_point = self.private_end_point
        path = self.get_order_path
        parameters = { "orderId": order_id }

        headers = self.make_headers(method, path)
        try:
            resp = requests.get(end_point + path, headers=headers, params=parameters)
            logger.error(f'action=get_order {resp.json()}')
            resp = resp.json()['data']['list'][0]

        except Exception as e:
            logger.error(f'action=get_order error={e}')
            raise

        if not resp:
            return resp

        order = Order(
            product_code=resp['symbol'],
            side=resp['side'],
            size=float(resp['size']),
            price=float(resp['price']),
            execution_type=resp['executionType'],
            status=resp['status'],
            order_id=resp['orderId']
        )
        return order

    def send_bulk_close_order(self, order):
        method = 'POST'
        end_point = self.private_end_point
        path = self.send_bulk_close_order_path
        if order.side == constants.BUY:
            side = 'SELL'
        if order.side == constants.SELL:
            side = 'BUY'

        request_body = {
            'symbol': order.product_code,
            'side': side,
            'executionType': 'MARKET',
            # 'price': order_price,
            'size': order.size,
        }
        headers = self.make_headers(method, path, request_body)
        try:
            resp = requests.post(end_point + path, headers=headers, data=json.dumps(request_body))
        except Exception as e:
            logger.error(f'action=send_bulk_close_order error={e}')
            raise

        return resp.json()['data']

    def send_cancel_order(self, order_id):
        method = 'POST'
        end_point = self.private_end_point
        path = self.send_cancel_order_path

        request_body = {
            'orderId':order_id,
        }
        
        headers = self.make_headers(method, path, request_body)
        try:
            resp = requests.post(end_point + path, headers=headers, data=json.dumps(request_body))
        except Exception as e:
            logger.error(f'action=send_cancel_order error={e}')
            raise
        
        return resp.json()['status']

    def send_cancel_orders(self, order_id):
        method = 'POST'
        end_point = self.private_end_point
        path = self.send_cancel_orders_path

        request_body = {
            'orderIds': [order_id],
        }
        
        headers = self.make_headers(method, path, request_body)
        try:
            resp = requests.post(end_point + path, headers=headers, data=json.dumps(request_body))
        except Exception as e:
            logger.error(f'action=send_cancel_orders error={e}')
            raise
        return resp.json()['data']['success']

    def send_cancel_bulk_order(self, order):
        method = 'POST'
        end_point = self.private_end_point
        path = self.send_cancel_bulk_order_path

        request_body = {
            'symbols':[order.product_code],
        }
        
        headers = self.make_headers(method, path, request_body)
        try:
            resp = requests.post(end_point + path, headers=headers, data=json.dumps(request_body))
        except Exception as e:
            logger.error(f'action=send_cancel_bulk_order error={e}')
            raise
        
        return resp.json()['data']

    def make_headers(self, method, path, request_body=None):
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        if request_body:
            text = timestamp + method + path + json.dumps(request_body)
        else:
            text = timestamp + method + path
        sign = hmac.new(bytes(self.api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.api_key,
            'API-TIMESTAMP': timestamp,
            'API-SIGN': sign
        }
        return headers

