# coding=utf-8
# !/usr/bin/env python

"""
@author: HU
@desc: 
"""
import datetime
import logging
import math
import os
import time
import traceback

import pytz
import telegram

from trade.hot_coin_api import HotCoin
from utils.config_loader import config
from utils.csv_tool import read_csv_file, save_csv

logger = logging.getLogger(__name__)

config.load_config()
bot = telegram.Bot(token=config.BOT_TOKEN)


def get_datetime(value, type='%Y%m%d%H%M%S'):
    return datetime.datetime.strptime(value, type)


def get_datetime_str(datetime_value, type='%Y%m%d%H%M%S'):
    return datetime_value.strftime(type)


def gen_volume_report():
    err_times = 0
    while True:
        try:
            config.load_config()
            hot_coin = HotCoin(symbol=config.SYMBOL)
            hot_coin.auth(key=config.ACCESS_KEY, secret=config.SECRET_KEY)
            ticker_data = hot_coin.get_ticker(step=60 * 60 * 4)
            if 'data' in ticker_data:
                ticker_data = ticker_data['data']
                now = datetime.datetime.now()
                now_hour = now.hour
                end_hour = 8 * math.floor(now_hour / 8)
                now_day = datetime.datetime.now().date()
                end_datetime = get_datetime(f'{now_day}{end_hour}0000', type='%Y-%m-%d%H%M%S')
                end_timestamp = end_datetime.timestamp()
                start_timestamp = end_timestamp - 60 * 60 * 8
                # start_datetime = datetime.datetime.fromtimestamp(start_timestamp, tz=pytz.timezone('Asia/Shanghai'))

                total_volume = float(0)
                for item in reversed(ticker_data):
                    if start_timestamp <= float(item[0]) / 1000 <= end_timestamp:
                        total_volume += float(item[5])
                volume_report_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv'),
                                                  'reportVolume.csv')
                volume_report = read_csv_file(volume_report_path)
                new_row_index = volume_report.shape[0]
                end_datetime_str = get_datetime_str(end_datetime, type='%Y-%m-%d %H:%M')
                volume_report.loc[new_row_index, 'datetime'] = end_datetime_str
                volume_report.loc[new_row_index, 'volume'] = round(total_volume, 5)
                save_csv(volume_report_path, volume_report)
                logger.info('生成 volume report')
                bot.send_document(chat_id=config.REPORT_TG_CHAT, document=open(volume_report_path, 'rb'),
                                  filename=f'#{config.SYMBOL_NAME} 统计交易量 {end_datetime_str}.csv')
                # bot.send_message(config.REPORT_TG_CHAT, f'#{config.SYMBOL_NAME} *统计交易量*\n'
                #                                         f'时间: {get_datetime_str(start_datetime, "%Y-%m-%d %H:%M")}'
                #                                         f' - {get_datetime_str(end_datetime, "%Y-%m-%d %H:%M")}\n'
                #                                         f'交易量: {round(total_volume, 5)}', parse_mode='Markdown')
                break
            else:
                logger.warning(f'Ticker信息获取错误, {ticker_data}')
                raise Exception
        except Exception as e:
            logger.error(e)
            err_times += 1
            traceback.print_exc()
            if err_times >= 3:
                break
            time.sleep(3)


def gen_assets_report():
    err_times = 0
    while True:
        try:
            config.load_config()
            now = datetime.datetime.now()
            now_day = datetime.datetime.now().date()
            report_hour = 8 * math.floor(now.hour / 8)
            report_datetime = get_datetime(f'{now_day}{report_hour}0000', type='%Y-%m-%d%H%M%S')
            report_datetime_str = get_datetime_str(report_datetime, '%Y-%m-%d %H:%M')
            bot_coin_balance, bot_usdt_balance = get_balance(config.ACCESS_KEY, config.SECRET_KEY)

            assets_report_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv'),
                                              'reportAssets.csv')
            assets_report = read_csv_file(assets_report_path)
            new_row_index = assets_report.shape[0]
            assets_report.loc[new_row_index, 'datetime'] = report_datetime_str
            assets_report.loc[new_row_index, 'bot_coin_balance'] = round(bot_coin_balance, 5)
            assets_report.loc[new_row_index, 'bot_usdt_balance'] = round(bot_usdt_balance, 5)
            assets_report.loc[new_row_index, 'total_coin_balance'] = round(bot_coin_balance, 5)
            assets_report.loc[new_row_index, 'total_usdt_balance'] = round(bot_usdt_balance, 5)
            for i in range(len(config.OTHER_ACCESS_KEYS)):
                other_coin_balance, other_usdt_balance = get_balance(config.OTHER_ACCESS_KEYS[i],
                                                                     config.OTHER_SECRET_KEYS[i])
                other_coin_balance_columns = f'user_{config.SYMBOL_NAME}_balance{i}'
                assets_report.loc[new_row_index, other_coin_balance_columns] = round(other_coin_balance, 5)
                assets_report.loc[new_row_index, 'total_coin_balance'] += round(other_coin_balance, 5)

                other_usdt_balance_columns = f'user_USDT_balance{i}'
                assets_report.loc[new_row_index, other_usdt_balance_columns] = round(other_usdt_balance, 5)
                assets_report.loc[new_row_index, 'total_usdt_balance'] += round(other_usdt_balance, 5)
            save_csv(assets_report_path, assets_report)
            logger.info('生成 assets report')
            bot.send_document(chat_id=config.REPORT_TG_CHAT, document=open(assets_report_path, 'rb'),
                              filename=f'#{config.SYMBOL_NAME} 统计资产 {report_datetime_str}.csv')
            break
        except Exception as e:
            logger.error(e)
            err_times += 1
            traceback.print_exc()
            if err_times >= 0:
                break
            time.sleep(3)


def gen_analyze_report():
    err_times = 0
    while True:
        try:
            config.load_config()
            now = datetime.datetime.now()
            now_day = datetime.datetime.now().date()
            report_datetime_str = get_datetime_str(now, '%Y-%m-%d %H:%M:%S')
            today_datetime = get_datetime(f'{now_day}000000', type='%Y-%m-%d%H%M%S')
            today_datetime_str = get_datetime_str(today_datetime, '%Y-%m-%d %H:%M')

            assets_report_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv'),
                                              'reportAssets.csv')

            analyze_report_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv'),
                                               'reportAnalyze.csv')

            # 获取今日初始资产
            assets_report = read_csv_file(assets_report_path)
            today_first_asset_report = assets_report.loc[assets_report['datetime'] == today_datetime_str]
            analyze_report = read_csv_file(analyze_report_path)
            new_row_index = analyze_report.shape[0]
            # 时间
            analyze_report.loc[new_row_index, 'datetime'] = report_datetime_str

            # 资产浮动1000判断
            if today_first_asset_report.empty:
                analyze_report.loc[new_row_index, 'asset_float'] = '-'
            else:
                today_total_usdt_balance = today_first_asset_report.loc[0, 'total_usdt_balance']

                # 获取当前资产
                bot_coin_balance, bot_usdt_balance = get_balance(config.ACCESS_KEY, config.SECRET_KEY)
                total_coin_balance = bot_coin_balance
                total_usdt_balance = bot_usdt_balance
                for i in range(len(config.OTHER_ACCESS_KEYS)):
                    other_coin_balance, other_usdt_balance = get_balance(config.OTHER_ACCESS_KEYS[i],
                                                                         config.OTHER_SECRET_KEYS[i])
                    total_coin_balance += other_coin_balance

                    total_usdt_balance += other_usdt_balance

                # 比较资产
                if total_usdt_balance - today_total_usdt_balance > 1000 or today_total_usdt_balance - total_usdt_balance > 1000:
                    analyze_report.loc[new_row_index, 'asset_float'] = 0
                else:
                    analyze_report.loc[new_row_index, 'asset_float'] = 1

            # 判断盘口
            analyze_report.loc[new_row_index, 'depth_check'] = get_depth_check()

            # 判断24小时成交量、趋势
            ticker_data = get_24h_ticker()
            analyze_report.loc[new_row_index, 'volume'] = ticker_data['vol']
            if float(ticker_data['high']) > config.ALERT_PRICE_MAX or float(
                    ticker_data['low']) < config.ALERT_PRICE_MIN:
                analyze_report.loc[new_row_index, 'trend'] = 0
            else:
                analyze_report.loc[new_row_index, 'trend'] = 1
            save_csv(analyze_report_path, analyze_report)
            logger.info('生成 analyze report')

            bot.send_document(chat_id=config.REPORT_TG_CHAT, document=open(analyze_report_path, 'rb'),
                              filename=f'#{config.SYMBOL_NAME} 分析对接 {report_datetime_str}.csv')
            break
        except Exception as e:
            logger.error(e)
            err_times += 1
            traceback.print_exc()
            if err_times >= 0:
                break
            time.sleep(3)


def get_balance(access_key, secret_key):
    hot_coin = HotCoin(symbol=config.SYMBOL)
    hot_coin.auth(key=access_key, secret=secret_key)
    account_info = hot_coin.get_account_info()
    coin_balance = 0
    usdt_balance = 0
    if 'data' in account_info and 'wallet' in account_info['data']:
        # return
        for item in account_info['data']['wallet']:
            if item['symbol'] == config.SYMBOL_NAME:
                coin_balance = item['total']
            if item['symbol'] == 'USDT':
                usdt_balance = item['total']
        return coin_balance, usdt_balance
    else:
        logger.warning(f'账号资产信息获取错误, {account_info}')
        raise Exception


def get_depth_check():
    hot_coin = HotCoin(symbol=config.SYMBOL)
    depth_data = hot_coin.get_depth()
    if 'data' in depth_data:
        flag = 1
        index = 0
        depth_list = depth_data['data']['depth']
        for price, item in depth_list['asks']:
            if index >= 20:
                break
            if not config.ALERT_PRICE_MAX > float(price) > config.ALERT_PRICE_MIN:
                return 0
            index += 1
        index = 0
        for price, item in depth_list['bids']:
            if index >= 20:
                break
            if not config.ALERT_PRICE_MAX > float(price) > config.ALERT_PRICE_MIN:
                return 0
            index += 1
        return flag
    else:
        logger.warning(f'深度请求错误, {depth_data}')
        raise Exception


def get_24h_ticker():
    hot_coin = HotCoin(symbol=config.SYMBOL)
    ticker_data = hot_coin.get_24h_ticker()
    if 'ticker' in ticker_data:
        for item in ticker_data['ticker']:
            if item['symbol'] == config.SYMBOL:
                return item
        logger.warning('找不到Symbol信息')
        raise Exception
    else:
        logger.warning(f'Ticker信息获取错误, {ticker_data}')
        raise Exception


if __name__ == '__main__':
    gen_volume_report()
    gen_assets_report()
    gen_analyze_report()
