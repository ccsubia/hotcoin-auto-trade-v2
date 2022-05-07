# !/usr/bin/env python
# coding=utf-8

"""
@author: HU
@desc:
"""
import functools
import logging
import os
from importlib import import_module

import telegram.bot
from telegram.ext import Updater, Dispatcher
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request as TGRequest

from utils.config_loader import config


class MQBot(telegram.bot.Bot):
    """A subclass of Bot which delegates send method handling to MQ"""

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue(
            all_burst_limit=29,
            all_time_limit_ms=1017,
            group_burst_limit=19,
            group_time_limit_ms=60000,
        )

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    def auto_group(method):
        @functools.wraps(method)
        def wrapped(self, *args, **kwargs):
            chat_id = 0
            if "chat_id" in kwargs:
                chat_id = kwargs["chat_id"]
            elif len(args) > 0:
                chat_id = args[0]
            if type(chat_id) is str:
                is_group = True
            else:
                is_group = (chat_id < 0)
            return method(self, *args, **kwargs, isgroup=is_group)

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""
        return super(MQBot, self).send_message(*args, **kwargs)

    @mq.queuedmessage
    def send_photo(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""
        return super(MQBot, self).send_photo(*args, **kwargs)

    #
    # @mq.queuedmessage
    # def edit_message_text(self, *args, **kwargs):
    #     '''Wrapped method would accept new `queued` and `isgroup`
    #     OPTIONAL arguments'''
    #     return super(MQBot, self).edit_message_text(*args, **kwargs)

    @mq.queuedmessage
    def forward_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""
        return super(MQBot, self).forward_message(*args, **kwargs)

    #
    # @mq.queuedmessage
    # def answer_callback_query(self, *args, **kwargs):
    #     '''Wrapped method would accept new `queued` and `isgroup`
    #     OPTIONAL arguments'''
    #     return super(MQBot, self).answer_callback_query(*args, **kwargs)

    @mq.queuedmessage
    def leave_chat(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""
        return super(MQBot, self).leave_chat(*args, **kwargs)


logger = logging.getLogger(__name__)


def main():
    try:
        logger.info('start bot')
        config.load_all_config()
        q = mq.MessageQueue()
        request = TGRequest(con_pool_size=8)
        my_bot = MQBot(config.BOT_TOKEN, request=request, mqueue=q)
        updater = Updater(bot=my_bot, use_context=True)

        load_handlers(updater.dispatcher)

        updater.start_polling()
        # updater.bot.send_message(chat_id=config.BOT_SUPER_ADMIN, text='HotCoin Telegram Bot, 启动!!')
        updater.idle()
    except Exception as e:
        logger.exception(e)


def load_handlers(dispatcher: Dispatcher):
    """Load handlers from files in a 'bot' directory."""
    base_path = os.path.join(os.path.dirname(__file__), 'handlers')
    files = os.listdir(base_path)

    for file_name in files:
        if file_name.endswith('.py'):
            handler_module, _ = os.path.splitext(file_name)
            if handler_module == 'process_message':
                continue

            module = import_module(f'tg.handlers.{handler_module}', 'handlers')
            module.init(dispatcher)
            logger.info('loaded handler module: {}'.format(handler_module))


if __name__ == '__main__':
    main()
