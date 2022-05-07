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
    dispatcher.add_handler(CommandHandler('self_trade_config_show', self_trade_config_show))
    dispatcher.add_handler(CommandHandler('set_self_trade_interval', set_self_trade_interval))
    dispatcher.add_handler(CommandHandler('set_self_tradeMin', set_self_tradeMin))
    dispatcher.add_handler(CommandHandler('set_self_tradeMax', set_self_tradeMax))


def self_trade_config_show(update, context):
    logger.info('self_trade_config_show')
    text = f'*#{config.SYMBOL_NAME} Self交易配置*\n' \
           f'交易间隔时间：{config.self_trade_interval}s\n' \
           f'交易数量区间：{config.self_tradeMin} - {config.self_tradeMax}'
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


@restricted_admin
def set_self_trade_interval(update, context):
    logger.info('set_self_trade_interval')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_self_trade_interval <间隔时间>')
        return
    config.self_trade_interval = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['self_trade_interval'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)


@restricted_admin
def set_self_tradeMin(update, context):
    logger.info('set_self_tradeMin')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_self_tradeMin <最小交易量>')
        return
    config.self_tradeMin = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['self_trade_min'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)


@restricted_admin
def set_self_tradeMax(update, context):
    logger.info('set_self_tradeMax')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_self_tradeMax <最大交易量>')
        return
    config.self_tradeMax = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['self_trade_max'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)
