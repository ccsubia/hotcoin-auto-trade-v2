# coding=utf-8
# !/usr/bin/env python

"""
@author: HU
@desc: 
"""
import logging
import traceback

import requests

from utils.config_loader import config

logger = logging.getLogger(__name__)


def remind_server_jiang(title, text):
    config.load_config()
    api = f'https://sctapi.ftqq.com/{config.SERVER_JIANG_TOKEN}.send'

    try:
        r = requests.request('GET', api, params={'title': title, 'desp': text})
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(err)
        return
    if r.status_code == 200:
        return r.json()


def remind_tg(chat, text):
    # config.load_config()
    api = f'https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage'

    try:
        r = requests.request('GET', api, params={'chat_id': chat, 'text': text})
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(err)
        return
    if r.status_code == 200:
        return r.json()


if __name__ == '__main__':
    try:
        # print(remind_tg(705788276, 'test'))
        print(remind_server_jiang('test', 'test'))
    except Exception as  e:
        traceback.print_exc()
