# -*- coding: utf-8 -*-
# #!/usr/bin/python
import logging

from telegram.ext import Dispatcher, CommandHandler

from tg.handlers.alert_price_config import alert_config_show
from tg.handlers.batch_push_trade_handler import pending_batch_push_trade_show, auto_batch_push_trade_show, \
    auto_batch_push_trade_show2, batch_push_trade_status_show
from tg.handlers.cancel_config import cancel_config_show
from tg.handlers.cross_trade_config import cross_trade_config_show
from tg.handlers.fork_trade_config import fork_trade_config_show
from tg.handlers.self_trade_config import self_trade_config_show

logger = logging.getLogger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('all_config_show', all_config_show))


def all_config_show(update, context):
    logger.info('all_config_show')
    alert_config_show(update, context)
    batch_push_trade_status_show(update, context)
    auto_batch_push_trade_show(update, context)
    auto_batch_push_trade_show2(update, context)
    pending_batch_push_trade_show(update, context)
    fork_trade_config_show(update, context)
    self_trade_config_show(update, context)
    cross_trade_config_show(update, context)
    cancel_config_show(update, context)
