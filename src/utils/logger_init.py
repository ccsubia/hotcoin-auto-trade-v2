# !/usr/bin/env python
# coding=utf-8

"""
@author: HU
@desc: 
"""
import logging
import os
import re
from logging import handlers
from pathlib import Path


def init_logger(log_name):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_logger.setFormatter(formatter)
    root_logger.addHandler(console_logger)

    this_file_name = os.path.basename(os.path.splitext(os.path.basename(log_name))[0])

    Path('./logs/').mkdir(parents=True, exist_ok=True)
    logfile = './logs/' + this_file_name

    file_logger = handlers.TimedRotatingFileHandler(logfile, encoding='utf-8', when='midnight')
    file_logger.suffix = "%Y-%m-%d.log"
    file_logger.extMatch = re.compile(r'^\d{4}-\d{2}-\d{2}\.log$')
    file_logger.setLevel(logging.DEBUG)
    file_logger.setFormatter(formatter)
    root_logger.addHandler(file_logger)

    logging.getLogger('telegram.bot').setLevel(logging.INFO)
    logging.getLogger('telegram.ext.dispatcher').setLevel(logging.INFO)
    logging.getLogger('telegram.ext.updater').setLevel(logging.INFO)
    logging.getLogger('telegram.vendor.ptb_urllib3.urllib3.connectionpool').setLevel(logging.INFO)
    logging.getLogger('JobQueue').setLevel(logging.INFO)

    return logfile
