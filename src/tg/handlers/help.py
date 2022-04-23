# -*- coding: utf-8 -*-
# #!/usr/bin/python
import logging
import os

from telegram.ext import Dispatcher, CommandHandler

logger = logging.getLogger(__name__)

help_md_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'md'), 'help.md')


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('help', help_fn))


def help_fn(update, context):
    logger.info('help')
    file = open(help_md_path, encoding='utf-8')
    text = file.read()
    rsp = update.message.reply_markdown(text)
    rsp.done.wait(timeout=60)
