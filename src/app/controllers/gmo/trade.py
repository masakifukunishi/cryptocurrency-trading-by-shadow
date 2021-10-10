import datetime
import logging
import time
import math
import pprint

import numpy as np

from gmo.gmo import APIClient
from gmo.gmo import Order

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)

class Trade(object):

    def __init__(self):
        self.API = APIClient(settings.gmo_api_key, settings.gmo_api_secret)
        self.product_code = settings.product_code
        self.use_coin = settings.use_coin
        self.target_size = settings.target_size

    def get_target_price(self, orderbooks, side):
        # 100円毎のグループを作成
        grouped_order = {}
        for orderbook in orderbooks:
            price, size = int(orderbook['price']), float(orderbook['size'])
            group = math.floor(price * 0.01) * 100
            if group in grouped_order:
                grouped_order[group] += size
            else:
                grouped_order[group] = size

        if side == constants.BUY: reverce = True
        if side == constants.SELL: reverce = False
        grouped_order = sorted(grouped_order.items(), key=lambda x: x[0], reverse=reverce)
        
        # グループの中から指定した数量以上の注文価格を取得
        target_group = 0
        for order in grouped_order:
            price, size = order[0], order[1]
            if size >= self.target_size:
                target_group = price
                break

        if not target_group:
            return None

        # 対象となったグループの中から数量が一番多い注文価格を取得
        max_size = 0
        for orderbook in orderbooks:
            price, size = int(orderbook['price']), float(orderbook['size'])
            group = math.floor(price * 0.01) * 100
            if group == target_group and max_size < size:
                target_price = price
                max_size = size

        if side == constants.BUY: target_price += 1 
        if side == constants.SELL: target_price -= 1 
        return target_price

    def get_best_price_orderbook(self):
        time.sleep(1)
        bids, asks = self.API.get_orderbooks()
        best_bid = int(bids[0]['price']) + 1
        best_ask = int(asks[0]['price']) - 1
        return best_bid, best_ask

    def send_order(self, side, price):
        order = Order(self.product_code, side, self.use_coin, price)
        order_id = self.API.send_order(order)
        # logger.info(f'action=send_order order_id={order_id}')
        return order_id

    def close_order(self, order_id):
        if not order_id:
            return

        while True:
            success = False
            order = self.API.get_order(order_id)
            close_id = None
            cancel_ids = []
            if order.status == 'EXECUTED':

                # best_bid, best_ask = self.get_best_price_orderbook()
                # if order.side == constants.BUY: order_price = best_bid
                # if order.side == constants.SELL: order_price = best_ask
                close_id = self.API.send_bulk_close_order(order)
                success = True
                logger.info(f'action=close_order type=close close_id={close_id}')
            else:
                cancel_ids = self.API.send_cancel_orders(order_id)
                logger.info(f'action=close_order type=cancel cancel_ids={cancel_ids}')
                time.sleep(0.25)
                order = self.API.get_order(order_id)
                if order.status == 'CANCELED':
                    success = True
            
            if success:
                logger.info(f'action=close_order statut=success order_status={order.status}')
                return

            logger.info(f'action=close_order statut=continue order_status={order.status}')

    def trade(self):
        while True:
            # get target price
            bids, _ = self.API.get_orderbooks()
            bid_order_id, ask_order_id = None, None
            # buy_order
            target_bid_price = self.get_target_price(bids, constants.BUY)
            if target_bid_price:
                bid_order_id = self.send_order(constants.BUY, target_bid_price)

            # sell_order
            _, asks = self.API.get_orderbooks()
            target_ask_price = self.get_target_price(asks, constants.SELL)
            if target_ask_price:
                ask_order_id = self.send_order(constants.SELL, target_ask_price)

            time.sleep(1.6)
            
            logger.info(f'action=close_order side=buy bid_order_id={bid_order_id}')
            self.close_order(bid_order_id)

            logger.info(f'action=close_order side=sell ask_order_id={ask_order_id}')
            self.close_order(ask_order_id)

            time.sleep(1)