# -*- coding:utf-8 -*-
# !/usr/bin/env python
import configparser
import logging
import os
import uuid
from collections import namedtuple
from datetime import datetime, timedelta

from telegram.ext import Dispatcher, CommandHandler

from trade.batch_push_trade import batch_push_trade
from trade.hot_coin_api import HotCoin
from utils.config_loader import config
from utils.csv_tool import read_csv_file, add_csv_rows, save_csv

logger = logging.getLogger(__name__)

raw_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')

pending_batch_push_trade_task = []


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('batch_push_trade_on', batch_push_trade_on))
    dispatcher.add_handler(CommandHandler('batch_push_trade_off', batch_push_trade_off))
    dispatcher.add_handler(CommandHandler('pending_batch_push_trade_show', pending_batch_push_trade_show))
    dispatcher.add_handler(CommandHandler('add_batch_push_trade', add_batch_push_trade))
    dispatcher.add_handler(CommandHandler('fast_add_batch_push_trade', fast_add_batch_push_trade))
    dispatcher.add_handler(CommandHandler('confirm_add_batch_push_trade', confirm_add_batch_push_trade))
    dispatcher.add_handler(CommandHandler('reset_pending_batch_push_trade', reset_pending_batch_push_trade))

    # dispatcher.add_handler(CommandHandler('default_batch_push_trade_config', default_period_config))


def check_admin(update):
    if update.effective_user.id in config.ADMINS:
        return True
    else:
        rsp = update.message.reply_text('仅管理员可调用此方法')
        rsp.done.wait(timeout=60)
        return False


def batch_push_trade_on(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('batch_push_trade_on')
    if not check_admin(update):
        return
    config.ALERT_PRICE_TG_ON = True
    raw_config['Trade']['batch_push_trade_on'] = 'True'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    text = '设置成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def batch_push_trade_off(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('batch_push_trade_off')
    if not check_admin(update):
        return
    config.ALERT_PRICE_TG_ON = False
    raw_config['Trade']['batch_push_trade_on'] = 'False'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    text = '设置成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def pending_batch_push_trade_show(update, context):
    logger.info('pending_batch_push_trade_show')
    print(pending_batch_push_trade_task)
    if not pending_batch_push_trade_task:
        text = '待确认批量挂单为空'
    else:
        text = f'*#{config.SYMBOL_NAME} 待确认批量挂单*'
        for item in pending_batch_push_trade_task:
            if item[0] == 1:
                type = '买单'
            else:
                type = '卖单'
            text = text + f"\n   类型: {type}\n" \
                          f"   挂单数: {item[1]}\n" \
                          f"   开始价格: {item[2]}\n" \
                          f"   价格间隔: {item[3]}\n" \
                          f"   开始数量: {item[4]}\n" \
                          f"   数量增量: {item[5]}\n" \
                          f"   间隔时间: {item[6]}\n"
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def add_batch_push_trade(update, context):
    logger.info('add_batch_push_trade')
    if not check_admin(update):
        return

    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/add_batch_push_trade', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if not len(params) == 7:
        text = '参数错误'
    else:
        BatchPushTrade = namedtuple('BatchPushTrade',
                                    ['type', 'push_count', 'start_price', 'price_step', 'push_first_amount',
                                     'up_amount', 'time_interval'])
        pending_batch_push_trade_task.append(BatchPushTrade(
            params[0],
            params[1],
            params[2],
            params[3],
            params[4],
            params[5],
            params[6]
        ))
        text = '添加成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)
    pending_batch_push_trade_show(update, context)


def fast_add_batch_push_trade(update, context):
    logger.info(fast_add_batch_push_trade)
    return


def confirm_add_batch_push_trade(update, context):
    logger.info('confirm_add_batch_push_trade')
    if not check_admin(update):
        return
    if not pending_batch_push_trade_task:
        rsp = update.message.reply_text('无待确认任务')
        rsp.done.wait(timeout=60)
        return
    elif not config.batch_push_trade_on:
        rsp = update.message.reply_text('批量挂单未开启')
        rsp.done.wait(timeout=60)
        return
    else:
        rsp = update.message.reply_text('确认成功, 开始执行挂单')
        rsp.done.wait(timeout=60)
        temp_pending_batch_push_trade_task = pending_batch_push_trade_task.copy()
        pending_batch_push_trade_task.clear()
        for item in temp_pending_batch_push_trade_task:
            batch_push_trade(
                item[0],
                item[1],
                item[2],
                item[3],
                item[4],
                item[5],
                item[6]
            )
        rsp = update.message.reply_text('执行结束')
        rsp.done.wait(timeout=60)


def reset_pending_batch_push_trade(update, context):
    logger.info('reset_pending_add_period_task')
    if not check_admin(update):
        return
    # if not pending_batch_push_trade_task:
    pending_batch_push_trade_task.clear()
    rsp = update.message.reply_text('重置成功')
    rsp.done.wait(timeout=60)
