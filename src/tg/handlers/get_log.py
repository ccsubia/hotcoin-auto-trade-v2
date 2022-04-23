# -*- coding: utf-8 -*-
# #!/usr/bin/python
import logging
import os

from telegram.ext import Dispatcher, CommandHandler

from utils.callback import callback_delete_message
from utils.config_loader import config

logger = logging.getLogger(__name__)

raw_config_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs'), 'trade_main')


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('get_log', get_log))


def get_log(update, context):
    logger.info('get_log')
    if update.effective_user.id in config.ADMINS:
        update.message.reply_document(document=open(raw_config_path, 'rb'))
