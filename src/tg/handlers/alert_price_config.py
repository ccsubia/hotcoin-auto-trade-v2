# -*- coding: utf-8 -*-
# #!/usr/bin/python
import configparser
import logging
import os

from telegram.ext import Dispatcher, CommandHandler
from utils.config_loader import config

logger = logging.getLogger(__name__)

raw_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('alert_tg_on', alert_tg_on))
    dispatcher.add_handler(CommandHandler('alert_tg_off', alert_tg_off))
    dispatcher.add_handler(CommandHandler('alert_server_jiang_on', alert_server_jiang_on))
    dispatcher.add_handler(CommandHandler('alert_server_jiang_off', alert_server_jiang_off))
    dispatcher.add_handler(CommandHandler('alert_config_show', alert_config_show))
    dispatcher.add_handler(CommandHandler('set_alert_price_min', set_alert_price_min))
    dispatcher.add_handler(CommandHandler('set_alert_price_max', set_alert_price_max))
    dispatcher.add_handler(CommandHandler('set_alert_price_interval_minute', set_alert_price_interval_minute))
    dispatcher.add_handler(CommandHandler('set_alert_price_tg_chat', set_alert_price_tg_chat))

    dispatcher.add_handler(CommandHandler('set_alert_vol_count_minute', set_alert_vol_count_minute))
    dispatcher.add_handler(CommandHandler('set_alert_vol_min', set_alert_vol_min))


def check_admin(update):
    if update.effective_user.id in config.ADMINS:
        return True
    else:
        rsp = update.message.reply_text('仅管理员可调用此方法')
        rsp.done.wait(timeout=60)
        return False


def set_alert_price_min(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('set_alert_price_min')
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_alert_price_min', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if params[0] == '':
        text = '参数错误'
    elif update.effective_user.id in config.ADMINS:
        config.ALERT_PRICE_MIN = float(params[0])
        raw_config['Alert']['alert_price_min'] = params[0]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'
    else:
        text = '仅管理员可调用此方法'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def set_alert_price_max(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('set_alert_price_max')
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_alert_price_max', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if params[0] == '':
        text = '参数错误'
    elif update.effective_user.id in config.ADMINS:
        config.ALERT_PRICE_MAX = float(params[0])
        raw_config['Alert']['alert_price_max'] = params[0]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'
    else:
        text = '仅管理员可调用此方法'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def set_alert_price_interval_minute(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('set_alert_price_interval_minute')
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_alert_price_interval_minute', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if params[0] == '':
        text = '参数错误'
    elif update.effective_user.id in config.ADMINS:
        config.ALERT_PRICE_INTERVAL_MINUTE = float(params[0])
        raw_config['Alert']['alert_price_interval_minute'] = params[0]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'
    else:
        text = '仅管理员可调用此方法'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def set_alert_price_tg_chat(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('set_alert_price_tg_chat')
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_alert_price_tg_chat', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if params[0] == '':
        text = '参数错误'
    elif update.effective_user.id in config.ADMINS:
        config.ALERT_PRICE_INTERVAL_MINUTE = float(params[0])
        raw_config['Alert']['alert_price_tg_chat'] = params[0]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'
    else:
        text = '仅管理员可调用此方法'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def alert_tg_on(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('alert_price_tg_on')
    if not check_admin(update):
        return
    config.ALERT_PRICE_TG_ON = True
    raw_config['Alert']['alert_price_tg_on'] = 'True'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    text = '设置成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def alert_tg_off(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('alert_tg_off')
    if not check_admin(update):
        return
    config.ALERT_PRICE_TG_ON = False
    raw_config['Alert']['alert_price_tg_on'] = 'False'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    text = '设置成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def alert_server_jiang_on(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('alert_server_jiang_on')
    if not check_admin(update):
        return
    config.ALERT_PRICE_SERVER_JIANG_ON = True
    raw_config['Alert']['alert_price_server_jiang_on'] = 'True'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    text = '设置成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def alert_server_jiang_off(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('alert_server_jiang_off')
    if not check_admin(update):
        return
    config.ALERT_PRICE_SERVER_JIANG_ON = False
    raw_config['Alert']['alert_price_server_jiang_on'] = 'False'
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    text = '设置成功'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def alert_config_show(update, context):
    logger.info('alert_config_show')
    text = f'*预警配置*\n' \
           f'价格区间 {config.ALERT_PRICE_MIN} - {config.ALERT_PRICE_MAX}\n' \
           f'价格预警间隔 {config.ALERT_PRICE_INTERVAL_MINUTE} 分钟\n' \
           f'交易量检测时间段 {config.alert_vol_count_minute} 分钟\n' \
           f'时间段内最小交易量：{config.alert_vol_min}\n' \
           f'Tg目标chat ID  {int(config.ALERT_PRICE_TG_CHAT)}\n' \
           f'Tg 提醒开启 {config.ALERT_PRICE_TG_ON}\n' \
           f'Server酱 提醒开启 {config.ALERT_PRICE_SERVER_JIANG_ON}\n'
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


def set_alert_vol_count_minute(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('set_alert_vol_count_minute')
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_alert_vol_count_minute', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if params[0] == '':
        text = '参数错误'
    elif update.effective_user.id in config.ADMINS:
        config.alert_vol_count_minute = float(params[0])
        raw_config['Alert']['alert_vol_count_minute'] = params[0]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'
    else:
        text = '仅管理员可调用此方法'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def set_alert_vol_min(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('set_alert_vol_min')
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/set_alert_vol_min', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if params[0] == '':
        text = '参数错误'
    elif update.effective_user.id in config.ADMINS:
        config.alert_vol_min = float(params[0])
        raw_config['Alert']['alert_vol_min'] = params[0]
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '设置成功'
    else:
        text = '仅管理员可调用此方法'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)
