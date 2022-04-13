# -*- coding: utf-8 -*-
# #!/usr/bin/python
import logging

from telegram.ext import Dispatcher, CommandHandler

from utils.callback import callback_delete_message

logger = logging.getLogger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('id', get_id))
    dispatcher.add_handler(CommandHandler('chat_id', get_chat_id))


def get_id(update, context):
    logger.info('get_id')
    rsp = update.message.reply_markdown(f'`{update.effective_user.id}`')
    rsp.done.wait(timeout=60)


def get_chat_id(update, context):
    logger.info('get_id')
    rsp = update.message.reply_markdown(f'`{update.message.chat_id}`')
    rsp.done.wait(timeout=60)