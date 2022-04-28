# -*- coding:utf-8 -*-
# !/usr/bin/env python
import logging
import time

from trade.hot_coin_api import HotCoin
from utils.config_loader import config

logger = logging.getLogger(__name__)


def batch_push_trade(type, push_count, start_price, price_step, push_first_amount, up_amount, time_interval):
    print_prefix = f'[Batch Push Trade ]'
    try:
        config.load_config()

        # Check TRADE_ON
        if not config.batch_push_trade_on:
            logger.warning(f'{print_prefix} turn off')
            return
        logger.info(f'{print_prefix} Start...')
        logger.debug(f'{type} {push_count} {start_price} {price_step} {push_first_amount} {up_amount} {time_interval}')

        # init API
        hot_coin = HotCoin(symbol=config.SYMBOL)
        hot_coin.auth(key=config.ACCESS_KEY, secret=config.SECRET_KEY)

        for i in range(int(push_count)):
            if int(type) == 1:
                if not config.ALERT_PRICE_MIN < float(start_price) - i * float(price_step) < config.ALERT_PRICE_MAX:
                    logger.warning(f'{print_prefix} 价格超出预警范围')
                    break
                logger.info(f'{print_prefix} 买单 {round(float(start_price) - i * float(price_step), 8)} {round(float(push_first_amount) + i * float(up_amount), 4)}')
                hot_coin.buy(round(float(start_price) - i * float(price_step), 8), round(float(push_first_amount) + i * float(up_amount), 4))
            else:
                if not config.ALERT_PRICE_MIN < float(start_price) + i * float(price_step) < config.ALERT_PRICE_MAX:
                    logger.warning(f'{print_prefix} 价格超出预警范围')
                    break
                logger.info(f'{print_prefix} 卖单 {round(float(start_price) + i * float(price_step), 8)} {round(float(push_first_amount) + i * float(up_amount), 4)}')
                hot_coin.sell(round(float(start_price) + i * float(price_step), 8), round(float(push_first_amount) + i * float(up_amount), 4))
            time.sleep(float(time_interval))

    except Exception as e:
        logger.error(f'{print_prefix} 发送错误')
        logger.exception(e)
