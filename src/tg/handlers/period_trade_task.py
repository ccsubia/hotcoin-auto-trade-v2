# -*- coding:utf-8 -*-
# !/usr/bin/env python
import configparser
import logging
import os
import uuid
from collections import namedtuple
from datetime import datetime, timedelta

from telegram.ext import Dispatcher, CommandHandler

from trade.hot_coin_api import HotCoin
from utils.config_loader import config
from utils.csv_tool import read_csv_file, add_csv_rows, save_csv

logger = logging.getLogger(__name__)

k_line_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'csv'),
                           'kLine.csv')
add_rows = []


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('all_period_task', all_period_task))
    dispatcher.add_handler(CommandHandler('current_period_task', current_period_task))
    dispatcher.add_handler(CommandHandler('next_period_task', next_period_task))
    dispatcher.add_handler(CommandHandler('add_period_task', add_period_task))
    dispatcher.add_handler(CommandHandler('fast_add_period_task', fast_add_period_task))
    dispatcher.add_handler(CommandHandler('confirm_add_period_task', confirm_add_period_task))
    dispatcher.add_handler(CommandHandler('pending_add_period_task', pending_add_period_task))
    dispatcher.add_handler(CommandHandler('reset_pending_add_period_task', reset_pending_add_period_task))
    dispatcher.add_handler(CommandHandler('close_period_task', close_period_task))
    dispatcher.add_handler(CommandHandler('open_period_task', open_period_task))
    dispatcher.add_handler(CommandHandler('close_period_trade', close_period_trade))
    dispatcher.add_handler(CommandHandler('open_period_trade', open_period_trade))
    dispatcher.add_handler(CommandHandler('default_period_config', default_period_config))
    dispatcher.add_handler(CommandHandler('current_price', current_price))


def get_datetime(value):
    return datetime.strptime(value, '%Y%m%d%H%M%S')


def get_datetime_str(datetime_value):
    return datetime_value.strftime('%Y%m%d%H%M%S')


def check_admin(update):
    if update.effective_user.id in config.ADMINS:
        return True
    else:
        rsp = update.message.reply_text('你没有管理员权限')
        rsp.done.wait(timeout=60)
        return False


def all_period_task(update, context):
    logger.info('all_period_task')
    k_line = read_csv_file(k_line_path)
    text = "*全部任务列表*"
    count = 0
    for index, row in k_line.iterrows():
        text = text + f"\n - 任务ID: `{row['uuid']}`\n" \
                      f"   开始时间: {row['start_time']}\n" \
                      f"   结束时间: {row['end_time']}\n" \
                      f"   目标价格: {row['target_price']}\n" \
                      f"   创建价格单数量区间: {row['period_trade_amount_min']} - {row['period_trade_amount_max']}\n" \
                      f"   最大交易数量: {row['max_trade_amount']}\n" \
                      f"   已交易数量: {row['traded_amount']}\n" \
                      f"   时间间隔: {row['trade_interval_time']}\n" \
                      f"   是否开启: {row['is_open']}\n"
        count = count + 1
    if count == 0:
        text = '任务列表为空'
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def current_period_task(update, context):
    logger.info('current_period_task')
    k_line = read_csv_file(k_line_path)
    text = "*当前任务*"
    count = 0
    for index, row in k_line.iterrows():
        start_timestamp = get_datetime(row['start_time']).timestamp()
        end_timestamp = get_datetime(row['end_time']).timestamp()
        now_timestamp = datetime.now().timestamp()
        if end_timestamp > now_timestamp > start_timestamp:
            text = text + f"\n - 任务ID: `{row['uuid']}`\n" \
                          f"   开始时间: {row['start_time']}\n" \
                          f"   结束时间: {row['end_time']}\n" \
                          f"   目标价格: {row['target_price']}\n" \
                          f"   创建价格单数量区间: {row['period_period_amount_min']} - {row['period_trade_amount_max']}\n" \
                          f"   最大交易数量: {row['max_trade_amount']}\n" \
                          f"   已交易数量: {row['traded_amount']}\n" \
                          f"   时间间隔: {row['trade_interval_time']}\n" \
                          f"   是否开启: {row['is_open']}\n"
            count = count + 1
            break
    if count == 0:
        text = '未找到正在执行任务'
    logger.info(text)
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def next_period_task(update, context):
    logger.info('next_period_task')
    k_line = read_csv_file(k_line_path)
    text = "*等待执行任务*"
    count = 0
    for index, row in k_line.iterrows():
        start_timestamp = get_datetime(row['start_time']).timestamp()
        end_timestamp = get_datetime(row['end_time']).timestamp()
        now_timestamp = datetime.now().timestamp()
        if start_timestamp > now_timestamp:
            count = count + 1
            text = text + f"\n - 任务ID: `{row['uuid']}`\n" \
                          f"   开始时间: {row['start_time']}\n" \
                          f"   结束时间: {row['end_time']}\n" \
                          f"   目标价格: {row['target_price']}\n" \
                          f"   创建价格单数量区间: {row['period_trade_amount_min']} - {row['period_trade_amount_max']}\n" \
                          f"   最大交易数量: {row['max_trade_amount']}\n" \
                          f"   已交易数量: {row['traded_amount']}\n" \
                          f"   时间间隔: {row['trade_interval_time']}\n" \
                          f"   是否开启: {row['is_open']}\n"
            count = count + 1
    if count == 0:
        text = '未找到等待执行任务'
    logger.info(text)
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def pending_add_period_task(update, context):
    logger.info('pending_add_period_task')
    text = '*待确认任务*'
    count = 0
    for item in add_rows:
        text = text + f"\n - 任务ID: `{item[0]}`\n" \
                      f"   开始时间: {item[1]}\n" \
                      f"   结束时间: {item[2]}\n" \
                      f"   目标价格: {item[3]}\n" \
                      f"   创建价格单数量区间: {item[4]} - {item[5]}\n" \
                      f"   最大交易数量: {item[6]}\n" \
                      f"   已交易数量: {item[7]}\n" \
                      f"   时间间隔: {item[8]}\n" \
                      f"   是否开启: {item[9]}\n"
        count = count + 1
    if count == 0:
        text = '未找到待确认任务'
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def add_period_task(update, context):
    logger.info('add_period_task')
    if not check_admin(update):
        return

    TradeTask = namedtuple('TradeTask',
                           ['uuid', 'start_time', 'end_time', 'target_price', 'period_trade_amount_min',
                            'period_trade_amount_max', 'max_trade_amount', 'traded_amount',
                            'trade_interval_time', 'is_open'])
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/add_period_task', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if not len(params) == 7:
        text = '参数错误'
    else:
        uuid_str = str(uuid.uuid4())[:18]
        start_time = params[0]
        end_time = params[1]
        target_price = params[2]
        period_trade_amount_min = params[3]
        period_trade_amount_max = params[4]
        max_trade_amount = params[5]
        trade_interval_time = params[6]
        add_rows.append(TradeTask(
            uuid_str,
            start_time,
            end_time,
            target_price,
            period_trade_amount_min,
            period_trade_amount_max,
            max_trade_amount,
            0,
            trade_interval_time,
            True
        ))
        text = 'added'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def fast_add_period_task(update, context):
    logger.info('fast_add_period_task')
    if not check_admin(update):
        return

    TradeTask = namedtuple('TradeTask',
                           ['uuid', 'start_time', 'end_time', 'target_price', 'period_trade_amount_min',
                            'period_trade_amount_max', 'max_trade_amount', 'traded_amount',
                            'trade_interval_time', 'is_open'])
    logger.info(update)
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/fast_add_period_task', '')
    params = params.replace(' ', '')
    params = params.split(',')
    logger.info(params)
    if not len(params) == 2:
        text = '参数错误'
    else:
        uuid_str = str(uuid.uuid4())[:18]
        start_time = get_datetime_str(datetime.now())
        end_time = get_datetime_str(datetime.now() + timedelta(minutes=int(params[0])))
        price = get_current_price()
        if price > 0:
            target_price = round(price + price * float(params[1]) / 100, 5)
        else:
            rsp = update.message.reply_text('当前价格获取错误')
            rsp.done.wait(timeout=60)
            return
        period_trade_amount_min = config.DEFAULT_PERIOD_TRADE_AMOUNT_MIN
        period_trade_amount_max = config.DEFAULT_PERIOD_TRADE_AMOUNT_MAX
        max_trade_amount = config.DEFAULT_PERIOD_MAX_TRADE_AMOUNT
        trade_interval_time = config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME
        is_open = config.DEFAULT_PERIOD_IS_OPEN
        add_rows.append(TradeTask(
            uuid_str,
            start_time,
            end_time,
            target_price,
            period_trade_amount_min,
            period_trade_amount_max,
            max_trade_amount,
            0,
            trade_interval_time,
            is_open
        ))
        text = '添加成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def confirm_add_period_task(update, context):
    logger.info('confirm_add_period_task')
    if not check_admin(update):
        return
    if len(add_rows) > 0:
        add_csv_rows(k_line_path, add_rows)
    add_rows.clear()
    rsp = update.message.reply_text('确认成功')
    rsp.done.wait(timeout=60)


def reset_pending_add_period_task(update, context):
    logger.info('reset_pending_add_period_task')
    if not check_admin(update):
        return
    add_rows.clear()
    rsp = update.message.reply_text('重置成功')
    rsp.done.wait(timeout=60)


def close_period_task(update, context):
    logger.info('close_period_task')
    if not check_admin(update):
        return
    k_line = read_csv_file(k_line_path)
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/close_period_task', '')
    params = params.replace(' ', '')
    params = params.split(',')
    for item in params:
        k_line.loc[k_line['uuid'] == item, 'is_open'] = False
    save_csv(k_line_path, k_line)
    rsp = update.message.reply_markdown('关闭成功')
    rsp.done.wait(timeout=60)


def open_period_task(update, context):
    logger.info('open_period_task')
    if not check_admin(update):
        return
    k_line = read_csv_file(k_line_path)
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/open_period_task', '')
    params = params.replace(' ', '')
    params = params.split(',')
    for item in params:
        k_line.loc[k_line['uuid'] == item, 'is_open'] = True
    save_csv(k_line_path, k_line)
    rsp = update.message.reply_markdown('开启成功')
    rsp.done.wait(timeout=60)


def open_period_trade(update, context):
    logger.info('open_period_trade')
    if not check_admin(update):
        return

    raw_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['period_trade_on'] = 'True'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)

    rsp = update.message.reply_text('开启成功')
    rsp.done.wait(timeout=60)


def close_period_trade(update, context):
    logger.info('close_period_trade')
    if not check_admin(update):
        return

    raw_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['period_trade_on'] = 'False'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)

    rsp = update.message.reply_text('关闭成功')
    rsp.done.wait(timeout=60)


def default_period_config(update, context):
    logger.info('default_period_config')
    text = '*Period默认配置\n*'
    text = text + f" 创建价格单数量区间: {config.DEFAULT_PERIOD_TRADE_AMOUNT_MIN} - {config.DEFAULT_PERIOD_TRADE_AMOUNT_MAX}\n" \
                  f" 最大交易数量: {config.DEFAULT_PERIOD_MAX_TRADE_AMOUNT}\n" \
                  f" 时间间隔: {config.DEFAULT_PERIOD_TRADE_INTERVAL_TIME}\n" \
                  f" 是否开启: {config.DEFAULT_PERIOD_IS_OPEN}\n"
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def current_price(update, context):
    logger.info('get_price')
    price = get_current_price()
    if price == 0:
        text = '价格获取失败'
    else:
        text = f'当前价格:{price}'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def get_current_price():
    hot_coin = HotCoin(symbol=config.SYMBOL)
    ticker_data = hot_coin.get_ticker(86400)
    if ticker_data['code'] == 200 and 'data' in ticker_data:
        price = float(ticker_data['data'][-1][4])
        price = round(price, config.price_decimal_num)
        return price
    else:
        price = 0
    return price
