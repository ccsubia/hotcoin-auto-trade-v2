# -*- coding:utf-8 -*-
# !/usr/bin/env python
import configparser
import json
import logging
import os
import time
import zlib
from datetime import datetime

import websockets
from websockets.exceptions import ConnectionClosedError

from trade import utils
from trade.batch_push_trade import batch_push_trade
from utils.config_loader import config
from utils.remind_func import remind_server_jiang, remind_tg

logger = logging.getLogger(__name__)

raw_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')


def get_datetime(value):
    return datetime.strptime(str(value), '%Y%m%d%H%M%S')


def get_datetime_str(datetime_value):
    return datetime_value.strftime('%Y%m%d%H%M%S')


async def alert_price(hot_coin, websocket):
    klineParam = '{"sub": "market.' + config.SYMBOL + '.kline.1m"}'
    await websocket.send(klineParam)
    self_cnt = 0
    while True:
        try:
            print_prefix = f'[Alert Price: {self_cnt}]'
            config.load_config()

            # Check PERIOD_TRADE_ON
            if not config.ALERT_PRICE_TG_ON and not config.ALERT_PRICE_SERVER_JIANG_ON:
                logger.warning(f'{print_prefix} Alert Price turn off , Sleep {config.ALERT_PRICE_INTERVAL_MINUTE} 分钟')
                time.sleep(config.ALERT_PRICE_INTERVAL_MINUTE)
            logger.info(f'{print_prefix} Start time {utils.get_now_time_str("%Y/%m/%d %H:%M:%S")}...')

            # Get Price
            try:
                recv_text = await websocket.recv()
                ret = zlib.decompress(recv_text, 16 + zlib.MAX_WBITS).decode('utf-8')
                ret = json.loads(ret)
                logger.info(ret)
                if 'ping' in ret:
                    await websocket.send('{"pong": "pong"}')
                if 'data' in ret:
                    data_price = float(ret['data'][0][4])
                else:
                    ticker_data = hot_coin.get_ticker(86400)
                    if ticker_data['code'] == 200 and 'data' in ticker_data:
                        data_price = float(ticker_data['data'][-1][4])
                    else:
                        logger.debug(ticker_data)
                        logger.warning(f'{print_prefix} 获取价格失败, 3秒后重试')
                        raise Exception
            except ConnectionClosedError as e:
                logger.warning(e)
                logger.warning(f'{print_prefix} websockets 连接断开, 3秒后重连')
                time.sleep(3)
                async with websockets.connect(config.WEBSOCKETS_API, ping_interval=None) as new_websocket:
                    logger.info(f'{print_prefix} 重新建立wss连接')
                    websocket = new_websocket
                    await websocket.send(klineParam)
                    continue

            # Alert
            if data_price > config.ALERT_PRICE_MAX or data_price < config.ALERT_PRICE_MIN:
                logger.info(f'{print_prefix} #{config.SYMBOL} 价格预警, 当前价格 {round(data_price, 5)}')
                if config.ALERT_PRICE_TG_ON:
                    remind_tg(config.ALERT_PRICE_TG_CHAT, f'#{config.SYMBOL} 价格预警, 当前价格 {round(data_price, 5)}'
                                                          f', {config.ALERT_PRICE_INTERVAL_MINUTE} 分钟后重试')
                raw_config = configparser.ConfigParser()
                raw_config.read(raw_config_path, encoding='utf-8')
                raw_config['Trade']['auto_batch_push_trade_type'] = str(0)
                raw_config['Trade']['auto_batch_push_trade_push_count'] = str(0)
                raw_config['Trade']['auto_batch_push_trade_start_price'] = str(0)
                raw_config['Trade']['auto_batch_push_trade_price_step'] = str(0)
                raw_config['Trade']['auto_batch_push_trade_push_first_amount'] = str(0)
                raw_config['Trade']['auto_batch_push_trade_up_amount'] = str(0)
                raw_config['Trade']['auto_batch_push_trade_time_interval'] = str(0)
                with open(raw_config_path, 'w') as configfile:
                    raw_config.write(configfile)
                batch_push_trade(
                    config.auto_batch_push_trade_type,
                    config.auto_batch_push_trade_push_count,
                    config.auto_batch_push_trade_start_price,
                    config.auto_batch_push_trade_price_step,
                    config.auto_batch_push_trade_push_first_amount,
                    config.auto_batch_push_trade_up_amount,
                    config.auto_batch_push_trade_time_interval
                )
                if config.ALERT_PRICE_SERVER_JIANG_ON:
                    remind_server_jiang(f'{config.SYMBOL} 价格预警, 当前价格  {round(data_price, 5)}', f'当前价格{round(data_price, 5)}')
            else:
                logger.info(f'{print_prefix} #{config.SYMBOL} 未触发价格预警{config.ALERT_PRICE_MIN} - {config.ALERT_PRICE_MAX}'
                            f', 当前价格 {round(data_price, 5)}')
            logger.info(f'{print_prefix} {config.ALERT_PRICE_INTERVAL_MINUTE} 分钟后重入')
            time.sleep(config.ALERT_PRICE_INTERVAL_MINUTE * 60)
            self_cnt += 1
        except Exception as e:
            logger.error(f'Alert Price: 未知错误, 3秒后重试')
            logger.exception(e)
            time.sleep(3)
            break
