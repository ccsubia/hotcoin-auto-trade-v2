#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from functools import wraps

from utils.callback import callback_delete_message
from utils.config_loader import config

logger = logging.getLogger(__name__)


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if not update.effective_user:
            return
        user_id = update.effective_user.id
        ban_list = context.bot_data.get('ban', [])
        # access control. comment out one or the other as you wish. otherwise you can use any of the following examples.
        # if user_id in ban_list:
        if user_id in ban_list or user_id not in config.USER_IDS:
            logger.info('Unauthorized access denied for {} {}.'
                        .format(update.effective_user.full_name, user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def restricted_super_admin(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if not update.effective_user:
            return
        user_id = update.effective_user.id
        if user_id != config.SUPER_ADMIN:
            logger.info("Unauthorized super admin access denied for {} {}.".format(update.effective_user.full_name, user_id))
            update.message.reply_text('仅超级管理员可调用此方法')
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def restricted_admin(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if not update.effective_user:
            logger.info(update.effective_user)
            return
        user_id = update.effective_user.id
        if user_id not in config.ADMINS:
            logger.info("Unauthorized admin access denied for {} {}.".format(update.effective_user.full_name, user_id))
            update.message.reply_text('仅管理员可调用此方法')
            return
        return func(update, context, *args, **kwargs)
    return wrapped
