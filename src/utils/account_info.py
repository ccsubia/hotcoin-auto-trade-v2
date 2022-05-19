# coding=utf-8
# !/usr/bin/env python

"""
@author: HU
@desc: 
"""
import logging

logger = logging.getLogger(__name__)


class _Account:
    def __init__(self):
        self._bot_usdt_balance = 0
        self._other_account_usdt_balance = []

    @property
    def BOT_USDT_BALANCE(self):
        return self._bot_usdt_balance

    @BOT_USDT_BALANCE.setter
    def BOT_USDT_BALANCE(self, val):
        self._bot_usdt_balance = val

    @property
    def OTHER_ACCOUNT_USDT_BALANCE(self):
        return self._other_account_usdt_balance

    @OTHER_ACCOUNT_USDT_BALANCE.setter
    def OTHER_ACCOUNT_USDT_BALANCE(self, val):
        self._other_account_usdt_balance = val


accountClass = _Account()
