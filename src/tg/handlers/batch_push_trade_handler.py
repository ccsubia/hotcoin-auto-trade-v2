# -*- coding:utf-8 -*-
# !/usr/bin/env python
import configparser
import logging
import os
from collections import namedtuple

from telegram.ext import Dispatcher, CommandHandler

from trade.batch_push_trade import batch_push_trade
from utils.config_loader import config

logger = logging.getLogger(__name__)

raw_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')

pending_batch_push_trade_task = []


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('batch_push_trade_on', batch_push_trade_on))
    dispatcher.add_handler(CommandHandler('batch_push_trade_off', batch_push_trade_off))
    dispatcher.add_handler(CommandHandler('batch_push_trade_status_show', batch_push_trade_status_show))
    dispatcher.add_handler(CommandHandler('pending_batch_push_trade_show', pending_batch_push_trade_show))
    dispatcher.add_handler(CommandHandler('add_batch_push_trade', add_batch_push_trade))
    dispatcher.add_handler(CommandHandler('fast_add_batch_push_trade', fast_add_batch_push_trade))
    dispatcher.add_handler(CommandHandler('confirm_add_batch_push_trade', confirm_add_batch_push_trade))
    dispatcher.add_handler(CommandHandler('reset_pending_batch_push_trade', reset_pending_batch_push_trade))

    dispatcher.add_handler(CommandHandler('auto_batch_push_trade_show', auto_batch_push_trade_show))
    dispatcher.add_handler(CommandHandler('set_auto_batch_push_trade', set_auto_batch_push_trade))
    dispatcher.add_handler(CommandHandler('reset_auto_batch_push_trade', reset_auto_batch_push_trade))
    dispatcher.add_handler(CommandHandler('auto_batch_push_trade_show2', auto_batch_push_trade_show2))
    dispatcher.add_handler(CommandHandler('set_auto_batch_push_trade2', set_auto_batch_push_trade2))
    dispatcher.add_handler(CommandHandler('reset_auto_batch_push_trade2', reset_auto_batch_push_trade2))

    dispatcher.add_handler(CommandHandler('default_batch_push_trade_show', default_batch_push_trade_show))
    dispatcher.add_handler(CommandHandler('set_default_batch_push_trade', set_default_batch_push_trade))


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
    config.batch_push_trade_on = True
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
    config.batch_push_trade_on = False
    raw_config['Trade']['batch_push_trade_on'] = 'False'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    text = '设置成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def batch_push_trade_status_show(update, context):
    text = f'#{config.SYMBOL_NAME} \n' \
           f'是否开启批量挂单：{config.batch_push_trade_on}'
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def pending_batch_push_trade_show(update, context):
    logger.info('pending_batch_push_trade_show')
    if not pending_batch_push_trade_task:
        text = f'#{config.SYMBOL_NAME} 待确认批量挂单为空'
    else:
        text = f'*#{config.SYMBOL_NAME} 待确认批量挂单*'
        for item in pending_batch_push_trade_task:
            if int(item[0]) == 1:
                type = '买单'
            else:
                type = '卖单'
            text = text + f"\n类型: {type}\n" \
                          f"挂单数: {item[1]}\n" \
                          f"开始价格: {item[2]}\n" \
                          f"价格间隔: {item[3]}\n" \
                          f"开始数量: {item[4]}\n" \
                          f"数量增量: {item[5]}\n" \
                          f"间隔时间: {item[6]}\n"
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


def auto_batch_push_trade_show(update, context):
    logger.info('auto_batch_push_trade_show')
    config.load_config()
    text = f'*#{config.SYMBOL_NAME} 超出最大价格，自动批量挂单配置*'
    if config.auto_batch_push_trade_type == 1:
        type = '买单'
    else:
        type = '卖单'
    text = text + f"\n类型: {type}\n" \
                  f"挂单数: {config.auto_batch_push_trade_push_count}\n" \
                  f"开始价格: {config.auto_batch_push_trade_start_price}\n" \
                  f"价格间隔: {config.auto_batch_push_trade_price_step}\n" \
                  f"开始数量: {config.auto_batch_push_trade_push_first_amount}\n" \
                  f"数量增量: {config.auto_batch_push_trade_up_amount}\n" \
                  f"间隔时间: {config.auto_batch_push_trade_time_interval}"
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def set_auto_batch_push_trade(update, context):
    logger.info('set_auto_batch_push_trade')
    if not check_admin(update):
        return

    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_auto_batch_push_trade', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if not len(params) == 7:
        text = '参数错误'
    else:
        config.auto_batch_push_trade_type = float(params[0])
        config.auto_batch_push_trade_push_count = float(params[1])
        config.auto_batch_push_trade_start_price = float(params[2])
        config.auto_batch_push_trade_price_step = float(params[3])
        config.auto_batch_push_trade_push_first_amount = float(params[4])
        config.auto_batch_push_trade_up_amount = float(params[5])
        config.auto_batch_push_trade_time_interval = float(params[6])

        raw_config = configparser.ConfigParser()
        raw_config.read(raw_config_path, encoding='utf-8')
        raw_config['Trade']['auto_batch_push_trade_type'] = params[0]
        raw_config['Trade']['auto_batch_push_trade_push_count'] = params[1]
        raw_config['Trade']['auto_batch_push_trade_start_price'] = params[2]
        raw_config['Trade']['auto_batch_push_trade_price_step'] = params[3]
        raw_config['Trade']['auto_batch_push_trade_push_first_amount'] = params[4]
        raw_config['Trade']['auto_batch_push_trade_up_amount'] = params[5]
        raw_config['Trade']['auto_batch_push_trade_time_interval'] = params[6]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'

    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)
    auto_batch_push_trade_show(update, context)


def default_batch_push_trade_show(update, context):
    logger.info('default_batch_push_trade_show')
    config.load_config()
    text = f'*#{config.SYMBOL_NAME} 默认批量挂单配置*'
    if config.default_batch_push_trade_type == 1:
        type = '买单'
    else:
        type = '卖单'
    text = text + f"\n类型: {type}\n" \
                  f"挂单数: {config.default_batch_push_trade_push_count}\n" \
                  f"开始价格: {config.default_batch_push_trade_start_price}\n" \
                  f"价格间隔: {config.default_batch_push_trade_price_step}\n" \
                  f"开始数量: {config.default_batch_push_trade_push_first_amount}\n" \
                  f"数量增量: {config.default_batch_push_trade_up_amount}\n" \
                  f"间隔时间: {config.default_batch_push_trade_time_interval}"
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def set_default_batch_push_trade(update, context):
    logger.info('set_default_batch_push_trade')
    if not check_admin(update):
        return

    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_default_batch_push_trade', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if not len(params) == 7:
        text = '参数错误'
    else:
        config.default_batch_push_trade_type = float(params[0])
        config.default_batch_push_trade_push_count = float(params[1])
        config.default_batch_push_trade_start_price = float(params[2])
        config.default_batch_push_trade_price_step = float(params[3])
        config.default_batch_push_trade_push_first_amount = float(params[4])
        config.default_batch_push_trade_up_amount = float(params[5])
        config.default_batch_push_trade_time_interval = float(params[6])

        raw_config = configparser.ConfigParser()
        raw_config.read(raw_config_path, encoding='utf-8')
        raw_config['Trade']['default_batch_push_trade_type'] = params[0]
        raw_config['Trade']['default_batch_push_trade_push_count'] = params[1]
        raw_config['Trade']['default_batch_push_trade_start_price'] = params[2]
        raw_config['Trade']['default_batch_push_trade_price_step'] = params[3]
        raw_config['Trade']['default_batch_push_trade_push_first_amount'] = params[4]
        raw_config['Trade']['default_batch_push_trade_up_amount'] = params[5]
        raw_config['Trade']['default_batch_push_trade_time_interval'] = params[6]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'

    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)
    default_batch_push_trade_show(update, context)


def reset_auto_batch_push_trade(update, context):
    logger.info('reset_auto_batch_push_trade')
    if not check_admin(update):
        return

    config.auto_batch_push_trade_type = 0
    config.auto_batch_push_trade_push_count = 0
    config.auto_batch_push_trade_start_price = 0
    config.auto_batch_push_trade_price_step = 0
    config.auto_batch_push_trade_push_first_amount = 0
    config.auto_batch_push_trade_up_amount = 0
    config.auto_batch_push_trade_time_interval = 0

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
    rsp = update.message.reply_text('重置成功')
    rsp.done.wait(timeout=60)


def auto_batch_push_trade_show2(update, context):
    logger.info('auto_batch_push_trade_show2')
    config.load_config()
    text = f'*#{config.SYMBOL_NAME} 超出最小价格，自动批量挂单配置*'
    if config.auto_batch_push_trade_type2 == 1:
        type = '买单'
    else:
        type = '卖单'
    text = text + f"\n类型: {type}\n" \
                  f"挂单数: {config.auto_batch_push_trade_push_count2}\n" \
                  f"开始价格: {config.auto_batch_push_trade_start_price2}\n" \
                  f"价格间隔: {config.auto_batch_push_trade_price_step2}\n" \
                  f"开始数量: {config.auto_batch_push_trade_push_first_amount2}\n" \
                  f"数量增量: {config.auto_batch_push_trade_up_amount2}\n" \
                  f"间隔时间: {config.auto_batch_push_trade_time_interval2}"
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def set_auto_batch_push_trade2(update, context):
    logger.info('set_auto_batch_push_trade2')
    if not check_admin(update):
        return

    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_auto_batch_push_trade2', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if not len(params) == 7:
        text = '参数错误'
    else:
        config.auto_batch_push_trade_type2 = float(params[0])
        config.auto_batch_push_trade_push_count2 = float(params[1])
        config.auto_batch_push_trade_start_price2 = float(params[2])
        config.auto_batch_push_trade_price_step2 = float(params[3])
        config.auto_batch_push_trade_push_first_amount2 = float(params[4])
        config.auto_batch_push_trade_up_amount2 = float(params[5])
        config.auto_batch_push_trade_time_interval2 = float(params[6])

        raw_config = configparser.ConfigParser()
        raw_config.read(raw_config_path, encoding='utf-8')
        raw_config['Trade']['auto_batch_push_trade_type2'] = params[0]
        raw_config['Trade']['auto_batch_push_trade_push_count2'] = params[1]
        raw_config['Trade']['auto_batch_push_trade_start_price2'] = params[2]
        raw_config['Trade']['auto_batch_push_trade_price_step2'] = params[3]
        raw_config['Trade']['auto_batch_push_trade_push_first_amount2'] = params[4]
        raw_config['Trade']['auto_batch_push_trade_up_amount2'] = params[5]
        raw_config['Trade']['auto_batch_push_trade_time_interval2'] = params[6]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'

    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)
    auto_batch_push_trade_show2(update, context)


def reset_auto_batch_push_trade2(update, context):
    logger.info('reset_auto_batch_push_trade2')
    if not check_admin(update):
        return

    config.auto_batch_push_trade_type2 = 1
    config.auto_batch_push_trade_push_count2 = 0
    config.auto_batch_push_trade_start_price2 = 0
    config.auto_batch_push_trade_price_step2 = 0
    config.auto_batch_push_trade_push_first_amount2 = 0
    config.auto_batch_push_trade_up_amount2 = 0
    config.auto_batch_push_trade_time_interval2 = 0

    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['auto_batch_push_trade_type2'] = str(1)
    raw_config['Trade']['auto_batch_push_trade_push_count2'] = str(0)
    raw_config['Trade']['auto_batch_push_trade_start_price2'] = str(0)
    raw_config['Trade']['auto_batch_push_trade_price_step2'] = str(0)
    raw_config['Trade']['auto_batch_push_trade_push_first_amount2'] = str(0)
    raw_config['Trade']['auto_batch_push_trade_up_amount2'] = str(0)
    raw_config['Trade']['auto_batch_push_trade_time_interval2'] = str(0)
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('重置成功')
    rsp.done.wait(timeout=60)


def fast_add_batch_push_trade(update, context):
    logger.info('fast_add_batch_push_trade')
    if not check_admin(update):
        return
    else:
        BatchPushTrade = namedtuple('BatchPushTrade',
                                    ['type', 'push_count', 'start_price', 'price_step', 'push_first_amount',
                                     'up_amount', 'time_interval'])
        pending_batch_push_trade_task.append(BatchPushTrade(
            config.default_batch_push_trade_type,
            config.default_batch_push_trade_push_count,
            config.default_batch_push_trade_start_price,
            config.default_batch_push_trade_price_step,
            config.default_batch_push_trade_push_first_amount,
            config.default_batch_push_trade_up_amount,
            config.default_batch_push_trade_time_interval
        ))
        text = '添加成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)
    pending_batch_push_trade_show(update, context)


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
