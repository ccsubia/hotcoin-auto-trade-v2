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
    dispatcher.add_handler(CommandHandler('cancel_config_show', cancel_config_show))
    dispatcher.add_handler(CommandHandler('set_cancel_adjustable_time', set_cancel_adjustable_time))
    dispatcher.add_handler(CommandHandler('set_cancel_before_order_minutes', set_cancel_before_order_minutes))


def cancel_config_show(update, context):
    logger.info('cancel_config_show')
    text = f'*#{config.SYMBOL_NAME} 撤单配置*\n' \
           f'撤单间隔时间：{config.cancel_adjustable_time}s\n' \
           f'委托单大于距当前：{config.cancel_before_order_minutes}分钟'
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)


@restricted_admin
def set_cancel_adjustable_time(update, context):
    logger.info('set_cancel_adjustable_time')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_cancel_adjustable_time <间隔时间>')
        return
    config.cancel_adjustable_time = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['cancel_adjustable_time'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)
    cancel_config_show(update, context)


@restricted_admin
def set_cancel_before_order_minutes(update, context):
    logger.info('set_cancel_before_order_minutes')
    if not context.args or not context.args[0].isdigit:
        update.message.reply_text('参数错误： /set_cancel_before_order_minutes <委托单大于距当前分钟数>')
        return
    if float(context.args[0]) <= 5:
        update.message.reply_text('参数错误：分钟数不能小于5')
        return
    config.cancel_before_order_minutes = float(context.args[0])
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    raw_config['Trade']['cancel_before_order_minutes'] = context.args[0]
    with open(raw_config_path, 'w') as configfile:
        raw_config.write(configfile)
    rsp = update.message.reply_text('设置成功')
    rsp.done.wait(timeout=60)
    cancel_config_show(update, context)
