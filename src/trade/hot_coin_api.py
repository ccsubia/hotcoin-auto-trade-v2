# -*- coding:UTF-8 -*-
# !/usr/bin/env python
import base64
import hashlib
import hmac
import logging
import traceback
import urllib
from collections import namedtuple
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


def get_utc_str():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def http_post_request(url, params, timeout=10):
    # lang valueRange ： en_US,ko_KR,zh_CN
    header = {'lang': 'en_US'}
    response = requests.post(url, params, timeout=timeout, headers=header)
    if response.status_code == 200:
        return response.json()
    else:
        return


def http_get_request(url, params, timeout=10):
    # lang valueRange ： en_US,ko_KR,zh_CN
    header = {'lang': 'zh_CN'}
    response = requests.get(url, params, timeout=timeout, headers=header)
    if response.status_code == 200:
        return response.json()
    else:
        return


class HotCoin:
    def __init__(self, API_HOST='api.hotcoinfin.com', symbol=""):
        self.secret = None
        self.key = None
        self.API_HOST = 'api.hotcoinfin.com'
        self.API_RUL = 'https://' + self.API_HOST + '/v1/'
        self.symbol = symbol
        if not self.symbol:
            logging.error("Init error, please add symbol")
        requests.packages.urllib3.disable_warnings()

    def auth(self, key, secret):
        self.key = bytes(key, 'utf-8')
        self.secret = bytes(secret, 'utf-8')

    def public_request(self, method, api_url, **payload):
        """request public url"""
        r_url = self.API_RUL + api_url
        # print(r_url)
        try:
            r = requests.request(method, r_url, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.error(err)
        if r.status_code == 200:
            return r.json()

    def paramsSign(self, params, paramsPrefix, accessSecret):
        host = self.API_HOST
        method = paramsPrefix['method'].upper()
        uri = paramsPrefix['uri']
        tempParams = urllib.parse.urlencode(sorted(params.items(), key=lambda d: d[0], reverse=False))
        payload = '\n'.join([method, host, uri, tempParams]).encode(encoding='UTF-8')
        # accessSecret = accessSecret.encode(encoding='UTF-8')
        return base64.b64encode(hmac.new(accessSecret, payload, digestmod=hashlib.sha256).digest())

    def api_key_request(self, method, API_URI, **params):
        """request a signed url"""
        if not self.key or not self.secret:
            logging.error("Please config api key and secret")
            exit(-1)
        params_to_sign = {'AccessKeyId': self.key,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': get_utc_str()}
        host_name = urllib.parse.urlparse(self.API_RUL).hostname
        host_name = host_name.lower()
        paramsPrefix = {"host": host_name, 'method': method, 'uri': '/v1/' + API_URI}
        params_to_sign.update(params)
        params_to_sign['Signature'] = self.paramsSign(params_to_sign, paramsPrefix, self.secret).decode(
            encoding='UTF-8')
        url = self.API_RUL + API_URI
        try:
            if method == 'GET':
                return http_get_request(url, params_to_sign, 10)
            elif method == 'POST':
                return http_post_request(url, params_to_sign, 10)
        except requests.exceptions.HTTPError as err:
            traceback.print_exc()

    def get_depth(self):
        """get market depth"""
        return self.public_request('GET', 'depth', symbol=self.symbol)

    def get_account_info(self):
        """get account info(done)"""
        return self.api_key_request('GET', 'balance')

    def create_order(self, **payload):
        """create order(done)"""
        return self.api_key_request('POST', 'order/place', **payload)

    def trade(self, price, amount, direction):
        """trade someting, buy(1) or sell(0)"""
        if direction == 1:
            return self.buy(price, amount)
        else:
            return self.sell(price, amount)

    def buy(self, price, amount):
        """buy someting(done)"""
        return self.create_order(symbol=self.symbol, type='buy', tradePrice=price, tradeAmount=amount)

    def sell(self, price, amount):
        """sell someting(done)"""
        return self.create_order(symbol=self.symbol, type='buy', tradePrice=price, tradeAmount=amount)

    def get_order(self, order_id):
        """get specfic order(done)"""
        return self.api_key_request('GET', 'order/detailById', id=order_id)

    def get_open_order(self):
        """get specfic order(done)"""
        return self.api_key_request('GET', 'order/entrust', symbol=self.symbol, type=1, count=100)

    def cancel_order(self, order_id):
        """cancel specfic order(done)"""
        return self.api_key_request('POST', 'order/cancel', id=order_id)

    def get_current_order(self):
        """get current orders"""
        return self.api_key_request('GET', 'order/entrust', symbol=self.symbol, type=1, count=100)

    def get_my_trade(self):
        """get my trades"""
        return self.api_key_request('GET', 'order/matchresults', symbol=self.symbol)

    def check_trade_status(self, order_ret):
        if 'code' in order_ret:
            if order_ret['code'] == 200:
                return True
            else:
                return False

    def check_depth_status(self, depth_ret):
        if 'data' in depth_ret and 'depth' in depth_ret['data'] and 'asks' in depth_ret['data']['depth'] and 'bids' in depth_ret['data']['depth']:
            return True
        else:
            return False

    def get_depth_list(self, depth_direction='asks'):
        depth_infos = self.get_depth()
        if self.check_depth_status(depth_infos):
            depth_infos = depth_infos['data']['depth'][depth_direction]
            if len(depth_infos) > 0:
                return depth_infos

    def get_ticker(self, step=60):
        return self.public_request('GET', 'ticker', symbol=self.symbol, step=step)


CancelRecord = namedtuple('CancelRecord', ['orderId', 'side', 'price', 'origQty', 'executedQty', 'time'])

if __name__ == "__main__":
    logging.info("Start...")
    from trade.default_config import config

    hot_coin = HotCoin(symbol=config['symbol'])
    hot_coin.auth(key=config['key'], secret=config['secret'])
    # logging.info(vaex.get_depth())
    while True:
        print(hot_coin.get_depth())
        # time.sleep(3)
    # logging.info(vaex.get_order(61964762655))
    # target_trade_action(vaex=vaex, adjusted_percent=0.01)
    # target_trade_allocation(vaex, 0.01, 0, 2)
