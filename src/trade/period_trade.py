# -*- coding:utf-8 -*-
# !/usr/bin/env python
import json
import logging
import os
import random
import time
import traceback
import zlib
from datetime import datetime

from websockets.exceptions import ConnectionClosedError

from trade import utils
from utils.config_loader import config
from utils.csv_tool import read_csv_file, save_csv, add_csv_rows

logger = logging.getLogger(__name__)

k_line_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv'), 'kLine.csv')
past_k_line_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv'), 'past_kLine.csv')


def get_datetime(value):
    return datetime.strptime(str(value), '%Y%m%d%H%M%S')


def get_datetime_str(datetime_value):
    return datetime_value.strftime('%Y%m%d%H%M%S')


async def period_trade(hot_coin, websocket):
    logger.info('start period trade')
    klineParam = '{"sub": "market.' + config.SYMBOL + '.kline.1m"}'
    await websocket.send(klineParam)
    self_cnt = 0
    while True:
        try:
            print_prefix = f'[Period Trade: {self_cnt}]'
            config.load_config()

            # Check PERIOD_TRADE_ON
            if not config.PERIOD_TRADE_ON:
                logger.warning('PERIOD_TRADE turn off')
                time.sleep(config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME)
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
                    logger.debug(ticker_data)
                    if ticker_data['code'] == 200 and 'data' in ticker_data:
                        data_price = float(ticker_data['data'][-1][4])
                    else:
                        logger.info(ticker_data)
                        logger.warning(f'{print_prefix} 获取价格失败, {config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME}秒后重试')
                        raise Exception
            except ConnectionClosedError as err:
                logger.warning(f'{print_prefix} websockets 连接断开, {config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME}秒后重连')
                time.sleep(config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME)
                await websocket.send(klineParam)
                continue

            # Read csv data
            k_line = read_csv_file(k_line_path)
            now = int(get_datetime_str(datetime.now()))
            past_k_line = k_line.loc[k_line['end_time'] < now]
            next_k_line = k_line.loc[k_line['end_time'] > now]
            have_task = False
            if next_k_line.empty:
                logger.warning(f'{print_prefix} 无匹配任务, {config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME}秒后重试')
                time.sleep(config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME)
                continue

            # Get Depth
            depth_data = hot_coin.get_depth()
            logger.debug(depth_data)
            if 'data' not in depth_data:
                logger.warning(f'{print_prefix} 深度获取失败')
                break

            # Run Task
            for index, row in next_k_line.iterrows():
                # Check open status
                if not bool(row['is_open']):
                    continue

                # Check time
                if not isinstance(row['start_time'], int) or not isinstance(row['end_time'], int):
                    continue
                if len(str(row['end_time'])) != 14 or len(str(row['start_time'])) != 14:
                    continue
                if not int(row['end_time']) > now > int(row['start_time']):
                    continue

                # Check should_trade_times
                end_timestamp = get_datetime(row['end_time']).timestamp()
                should_trade_times = int((end_timestamp - datetime.now().timestamp()) / row['trade_interval_time'])
                if should_trade_times < 1:
                    continue

                # Calculate price and amount
                target_price = float(row['target_price'])
                trade_price = round(data_price + (target_price - data_price) / should_trade_times, 5)
                depth_list = depth_data['data']['depth']
                if trade_price > data_price:
                    direction = 1
                    trade_amount = 0
                    depth_list = depth_list['asks']
                else:
                    direction = -1
                    trade_amount = 0
                    depth_list = depth_list['bids']
                for item in depth_list:
                    if (direction == 1 and trade_price < float(item[0])) or (
                            direction == -1 and trade_price > float(item[0])):
                        break
                    trade_amount += float(item[1])
                put_trade_amount = round(random.uniform(row['period_trade_amount_min'], row['period_trade_amount_max']),
                                         2)
                trade_amount = round(trade_amount + put_trade_amount, 2)
                new_traded_amount = round(row['traded_amount'] + put_trade_amount + trade_amount, 2)
                logger.debug(f'{print_prefix} trade_price: {trade_price}, put_trade_amount: {put_trade_amount}, '
                             f'trade_amount: {trade_amount}, new_traded_amount: {new_traded_amount}')

                # Check max_trade_amount
                if new_traded_amount > row['max_trade_amount']:
                    logger.warning(f'{print_prefix} 超过此时间段最大可交易数量')
                    continue

                # Trade flag and send trade
                have_task = True
                side_str1 = '买单' if direction == -1 else '卖单'
                side_str2 = '卖单' if direction == 1 else '买单'
                logger.info(f'{print_prefix} 下单方向:{side_str1}, 价格:{put_trade_amount}, 下单量:{put_trade_amount}')
                # result = hot_coin.trade(trade_price, put_trade_amount, 0 - direction)
                # result1Id = result['data']['ID']
                logger.info(f'{print_prefix} 下单方向:{side_str2}, 价格:{trade_price}, 下单量:{trade_amount}')
                # result = hot_coin.trade(trade_price, trade_amount, direction)
                # print(hot_coin.get_order(result1Id))
                # print(hot_coin.get_order(result['data']['ID']))

                # Update traded_amount
                next_k_line.loc[index, 'traded_amount'] = new_traded_amount
                if not past_k_line.empty:
                    add_csv_rows(past_k_line_path, past_k_line)
                save_csv(k_line_path, next_k_line)

                # Sleep
                logger.info(f'{print_prefix} {row["trade_interval_time"]} 秒后重新进入')
                time.sleep(row['trade_interval_time'])
                self_cnt += 1
                break
            if not have_task:
                logger.warning(f'{print_prefix} 无匹配任务, {config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME}秒后重试')
                time.sleep(config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME)
        except Exception as e:
            logger.error(e)
            logger.error(f'Period Trade: 未知错误, {config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME} 秒后重试')
            traceback.print_exc()
            time.sleep(config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME)
            break
