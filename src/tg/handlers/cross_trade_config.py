# -*- coding: utf-8 -*-
# #!/usr/bin/python
import configparser
import logging
import os

from telegram.ext import Dispatcher, CommandHandler
from utils.config_loader import config
from utils.restricted import restricted_admin

logger = logging.getLogger(__name__)

raw_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('cross_trade_config_show', cross_trade_config_show))
    dispatcher.add_handler(CommandHandler('set_cross_trade_interval', set_cross_trade_interval))
    dispatcher.add_handler(CommandHandler('set_cross_tradeMin', set_cross_tradeMin))
    dispatcher.add_handler(CommandHandler('set_cross_tradeMax', set_cross_tradeMax))
    dispatcher.add_handler(CommandHandler('set_cross_trade_price_min', set_cross_trade_price_min))
    dispatcher.add_handler(CommandHandler('set_cross_trade_price_max', set_cross_trade_price_max))
    dispatcher.add_handler(CommandHandler('set_cross_depth', set_cross_depth))


def cross_trade_config_show(update, context):
    logger.info('cross_trade_config_show')
    text = f'*#{config.SYMBOL_NAME} Cross交易配置*\n' \
           f'交易间隔时间：{config.cross_trade_interval}s\n' \
           f'盘口深度：{config.cross_depth}\n' \
           f'交易数量区间：{config.cross_tradeMin} - {config.cross_tradeMax}\n' \
           f'交易价格区间：{config.cross_trade_price_min} - {config.cross_trade_price_max}'
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


@restricted_admin
def set_cross_trade_interval(update, context):
    logger.info('set_cross_trade_interval')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_cross_trade_interval <间隔时间>')
        return
    config.cross_trade_interval = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['cross_trade_interval'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)


@restricted_admin
def set_cross_tradeMin(update, context):
    logger.info('set_cross_tradeMin')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_cross_tradeMin <最小交易量>')
        return
    config.cross_tradeMin = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['cross_trade_min'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)


@restricted_admin
def set_cross_tradeMax(update, context):
    logger.info('set_cross_tradeMax')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_cross_tradeMax <最大交易量>')
        return
    config.cross_tradeMax = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['cross_trade_max'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)


@restricted_admin
def set_cross_trade_price_min(update, context):
    logger.info('set_cross_trade_price_min')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_cross_trade_price_min <最小价格>')
        return
    config.cross_trade_price_min = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['cross_trade_price_min'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)


@restricted_admin
def set_cross_trade_price_max(update, context):
    logger.info('set_cross_trade_price_max')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_cross_trade_price_max <最大价格>')
        return
    config.cross_trade_price_max = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['cross_trade_price_max'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)


@restricted_admin
def set_cross_depth(update, context):
    logger.info('set_cross_depth')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_cross_depth <深度>')
        return
    config.cross_depth = int(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['cross_depth'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)
