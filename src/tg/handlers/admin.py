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
    dispatcher.add_handler(CommandHandler('add_admin', add_admin))
    dispatcher.add_handler(CommandHandler('rm_admin', rm_admin))
    dispatcher.add_handler(CommandHandler('admin_list', admin_list))


def add_admin(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('add_admin')
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/add_admin', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if params[0] == '':
        text = '参数错误'
    elif int(update.effective_user.id) == int(config.SUPER_ADMIN):
        config.ADMINS.append(int(params[0]))
        raw_config['Admin']['admins'] = ','.join(map(str, config.ADMINS))
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '添加成功'
    else:
        text = '仅超级管理员可添加管理员'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def rm_admin(update, context):
    raw_config = configparser.ConfigParser()
    raw_config.read(raw_config_path, encoding='utf-8')
    logger.info('rm_admin')
    params = update.message.text.replace(f'@{config.BOT_NAME}', '')
    params = params.replace('/rm_admin', '')
    params = params.replace(' ', '')
    params = params.split(',')
    if params[0] == '':
        text = '参数错误'
    elif int(update.effective_user.id) == int(config.SUPER_ADMIN):
        config.ADMINS.remove(int(params[0]))
        raw_config['Admin']['admins'] = ','.join(map(str, config.ADMINS))
        with open(raw_config_path, 'w') as configfile:
            raw_config.write(configfile)
        text = '移除成功'
    else:
        text = '仅超级管理员可移除管理员'
    rsp = update.message.reply_text(text)
    rsp.done.wait(timeout=60)


def admin_list(update, context):
    logger.info('admin_list')
    rsp = update.message.reply_text(config.ADMINS)
    rsp.done.wait(timeout=60)
