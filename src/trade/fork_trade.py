# -*- coding:utf-8 -*-
# !/usr/bin/env python
import json
import logging
import random
import time
import zlib
from datetime import datetime

import websockets
from websockets.exceptions import ConnectionClosedError

from trade import utils
from trade.hot_coin_api import HotCoin
from utils.config_loader import config
from utils.remind_func import remind_tg

logger = logging.getLogger(__name__)


def get_datetime(value):
    return datetime.strptime(str(value), '%Y%m%d%H%M%S')


def get_datetime_str(datetime_value):
    return datetime_value.strftime('%Y%m%d%H%M%S')


async def fork_trade(hot_coin, fork_coin_websocket):
    logger.info('enter fork trade')
    fork_coin_kline_param = '{"sub": "market.btc_usdt.kline.1m"}'

    '''# self_coin_kline_param = '{"sub": "market.' + config.SYMBOL + '.kline.1m"}'
    # async with websockets.connect(config.WEBSOCKETS_API, ping_interval=None) as new_websocket:
    #     self_coin_websocket = new_websocket
        # time.sleep(1)
    # await self_coin_websocket.send(self_coin_kline_param)'''
    await fork_coin_websocket.send(fork_coin_kline_param)

    self_cnt = 0
    fork_coin_scale = 0
    while True:
        try:
            print_prefix = f'[Fork Trade: {self_cnt}]'
            config.load_config()

            # Check fork_trade_on
            if not config.fork_trade_on:
                logger.warning('fork_trade 关闭, 10秒后重试')
                time.sleep(10)
                continue
            logger.info(f'{print_prefix} Start time {utils.get_now_time_str("%Y/%m/%d %H:%M:%S")}...')

            # Get Fork Coin Price
            try:
                fork_coin_recv_text = await fork_coin_websocket.recv()
                fork_coin_ret = zlib.decompress(fork_coin_recv_text, 16 + zlib.MAX_WBITS).decode('utf-8')
                fork_coin_ret = json.loads(fork_coin_ret)
                logger.info(fork_coin_ret)
                if 'ping' in fork_coin_ret:
                    await fork_coin_websocket.send('{"pong": "pong"}')
                if 'data' in fork_coin_ret:
                    fork_coin_data_price = float(fork_coin_ret['data'][0][4])
                else:
                    fork_coin_ticker_data = HotCoin(symbol='btc_usdt').get_ticker(86400)
                    if fork_coin_ticker_data['code'] == 200 and 'data' in fork_coin_ticker_data:
                        fork_coin_data_price = float(fork_coin_ticker_data['data'][-1][4])
                        logger.info(f'fork_coin_data_price: {fork_coin_data_price}')
                    else:
                        logger.warning(fork_coin_ticker_data)
                        logger.warning(f'{print_prefix} 获取价格失败')
                        raise Exception
            except ConnectionClosedError as e:
                logger.warning(e)
                logger.warning(f'{print_prefix} websockets 连接断开, 3秒后重连')
                time.sleep(3)
                async with websockets.connect(config.WEBSOCKETS_API, ping_interval=None) as new_websocket:
                    logger.info(f'{print_prefix} 重新建立wss连接')
                    fork_coin_websocket = new_websocket
                    await fork_coin_websocket.send(fork_coin_kline_param)
                    continue
            # Get Self Coin Price
            '''self_coin_recv_text = await self_coin_websocket.recv()
            self_coin_ret = zlib.decompress(self_coin_recv_text, 16 + zlib.MAX_WBITS).decode('utf-8')
            self_coin_ret = json.loads(self_coin_ret)
            logger.debug(self_coin_ret)
            if 'ping' in self_coin_ret:
                await self_coin_websocket.send('{"pong": "pong"}')
            if 'data' in self_coin_ret:
                self_coin_data_price = float(self_coin_ret['data'][0][4])
                logger.info(f'self_coin_data_price: {self_coin_data_price}')
            else:
                logger.debug(self_coin_ret)'''
            self_coin_ticker_data = hot_coin.get_ticker(86400)
            if self_coin_ticker_data['code'] == 200 and 'data' in self_coin_ticker_data:
                self_coin_data_price = float(self_coin_ticker_data['data'][-1][4])
                logger.info(f'self_coin_data_price: {self_coin_data_price}')
            else:
                logger.warning(self_coin_ticker_data)
                logger.warning(f'{print_prefix} 获取价格失败')
                raise Exception

            # Get Depth
            fork_coin_depth_data = HotCoin(symbol='btc_usdt').get_depth()
            self_coin_depth_data = hot_coin.get_depth()
            # logger.info(fork_coin_depth_data)
            # logger.info(self_coin_depth_data)
            if 'data' not in fork_coin_depth_data:
                logger.warning(f'{print_prefix} 深度获取失败')
                continue
            if 'data' not in self_coin_depth_data:
                logger.warning(f'{print_prefix} 深度获取失败')
                continue
            if fork_coin_scale == 0:
                fork_coin_scale = self_coin_data_price / fork_coin_data_price
                logger.info(f'{print_prefix} new fork_coin_scale : {fork_coin_scale}')
            fork_coin_scale = float(fork_coin_scale)
            # print('fork_coin_scale', fork_coin_scale)
            # Current Price
            # print('fork_coin_data_price', fork_coin_data_price)
            # print('self_coin_data_price', self_coin_data_price)

            # Fork Depth Price
            fork_coin_b1_price = float(fork_coin_depth_data['data']['depth']['bids'][0][0])
            # print('fork_coin_b1_price', fork_coin_b1_price)
            fork_coin_s1_price = float(fork_coin_depth_data['data']['depth']['asks'][0][0])
            # print('fork_coin_s1_price', fork_coin_s1_price)

            # Self Depth Amount 1
            self_coin_b1_amount = float(self_coin_depth_data['data']['depth']['bids'][0][1])
            # print('self_coin_b1_amount', self_coin_b1_amount)
            self_coin_s1_amount = float(self_coin_depth_data['data']['depth']['asks'][0][1])
            # print('self_coin_s1_amount', self_coin_s1_amount)

            # Self Trade Price
            self_coin_trade_b1_price = fork_coin_b1_price * fork_coin_scale
            # print('self_coin_trade_b1_price', self_coin_trade_b1_price)
            self_coin_trade_s1_price = fork_coin_s1_price * fork_coin_scale
            # print('self_coin_trade_s1_price', self_coin_trade_s1_price)

            # 发起卖单，消耗买单1
            trade_b1_price = round(self_coin_trade_b1_price, 8)
            trade_b1_amount = round(self_coin_b1_amount * 1.1, 4)
            trade_b1_type = 0
            # print('trade_b1_price', trade_b1_price, 'trade_b1_amount', trade_b1_amount, 'trade_b1_type', trade_b1_type)

            # 发起买单，消耗卖单1
            trade_s1_price = round(self_coin_trade_s1_price, 8)
            trade_s1_amount = round(self_coin_s1_amount * 1.1, 4)
            trade_s1_type = 1
            # print('trade_s1_price', trade_s1_price, 'trade_s1_amount', trade_s1_amount, 'trade_s1_type', trade_s1_type)

            trade_all_list = []
            # 挂单交易买一卖一
            if trade_b1_price < self_coin_data_price:
                trade_all_list.append({'price': trade_s1_price, 'amount': trade_s1_amount, 'trade_type': trade_s1_type})
                trade_all_list.append({'price': trade_b1_price, 'amount': trade_b1_amount, 'trade_type': trade_b1_type})
            else:
                trade_all_list.append({'price': trade_b1_price, 'amount': trade_b1_amount, 'trade_type': trade_b1_type})
                trade_all_list.append({'price': trade_s1_price, 'amount': trade_s1_amount, 'trade_type': trade_s1_type})

            # 挂单买卖2-3
            for i in range(2):
                push_sell_price = float(fork_coin_depth_data['data']['depth']['asks'][i + 1][0]) * fork_coin_scale
                push_sell_price = round(push_sell_price, 8)
                push_sell_amount = round(random.uniform(config.fork_trade_random_amount_min, config.fork_trade_random_amount_max), 4)
                trade_all_list.append({'price': push_sell_price, 'amount': push_sell_amount, 'trade_type': 0})

                push_buy_price = float(fork_coin_depth_data['data']['depth']['bids'][i + 1][0]) * fork_coin_scale
                push_buy_price = round(push_buy_price, 8)
                push_buy_amount = round(random.uniform(config.fork_trade_random_amount_min, config.fork_trade_random_amount_max), 4)
                trade_all_list.append({'price': push_buy_price, 'amount': push_buy_amount, 'trade_type': 1})

            # 校验限制
            check_error_flag = False
            for item in trade_all_list:
                if not config.ALERT_PRICE_MAX > item["price"] > config.ALERT_PRICE_MIN:
                    logger.warning(f'{print_prefix}交易价格超出预警区间, 价格: {item["price"]}')
                    remind_tg(config.ALERT_PRICE_TG_CHAT, f'{print_prefix}交易价格超出预警区间, 价格: {item["price"]}')
                    check_error_flag = True
                    break
                if item["amount"] > config.fork_trade_amount_max:
                    logger.warning(f'{print_prefix}交易量超额, 交易量：{item["amount"]}')
                    remind_tg(config.ALERT_PRICE_TG_CHAT, f'{print_prefix}交易量超额, 交易量：{item["amount"]}')
                    check_error_flag = True
                    break
            if check_error_flag:
                time.sleep(30)
                break

            # 发送交易
            for item in trade_all_list:
                logger.info(f'{print_prefix} 下单方向:{item["trade_type"]}, 价格:{item["price"]}, 下单量:{item["amount"]}')
                # result = hot_coin.trade(item["price"], item["amount"], item["trade_type"])
                # resultId = result['data']['ID']
                # logger.info(f'{print_prefix} 下单成功， ID：{resultId}')
                # print(hot_coin.get_order(resultId))
            # Sleep
            logger.info(f'{print_prefix} 交易完成等待重新进入')
            time.sleep(2)
            self_cnt += 1
            continue
        except Exception as e:
            logger.error(f'Fork Trade: 未知错误')
            logger.exception(e)
            time.sleep(1)
            break
