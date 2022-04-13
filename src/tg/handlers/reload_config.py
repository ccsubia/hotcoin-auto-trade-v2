# -*- coding: utf-8 -*-
# #!/usr/bin/python
import logging

from telegram.ext import Dispatcher, CommandHandler

from utils.callback import callback_delete_message
from utils.config_loader import config

logger = logging.getLogger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('reload_config', reload_config))


def reload_config(update, context):
    logger.info('reload_config')
    config.load_config()
    rsp = update.message.reply_text(config.ADMINS)
    rsp.done.wait(timeout=60)
    message_id = rsp.result().message_id
    if update.message.chat_id < 0:
        context.job_queue.run_once(callback_delete_message, 10,
                                   context=(update.message.chat_id, message_id))
        context.job_queue.run_once(callback_delete_message, 10,
                                   context=(update.message.chat_id, update.message.message_id))
