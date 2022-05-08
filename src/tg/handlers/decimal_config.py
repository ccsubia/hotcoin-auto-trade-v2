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
    dispatcher.add_handler(CommandHandler('decimal_config_show', decimal_config_show))
    dispatcher.add_handler(CommandHandler('set_price_decimal_num', set_price_decimal_num))
    dispatcher.add_handler(CommandHandler('set_vol_decimal_num', set_vol_decimal_num))


def decimal_config_show(update, context):
    logger.info('decimal_config_show')
    text = f'*#{config.SYMBOL_NAME} 精度配置*\n' \
           f'价格精度位数：{config.price_decimal_num}\n' \
           f'交易量精度位数：{config.vol_decimal_num}'
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


@restricted_admin
def set_price_decimal_num(update, context):
    logger.info('set_price_decimal_num')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_price_decimal_num <精度位数>')
        return
    config.price_decimal_num = int(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['price_decimal_num'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)


@restricted_admin
def set_vol_decimal_num(update, context):
    logger.info('set_vol_decimal_num')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_vol_decimal_num <精度位数>')
        return
    config.vol_decimal_num = int(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['vol_decimal_num'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)
