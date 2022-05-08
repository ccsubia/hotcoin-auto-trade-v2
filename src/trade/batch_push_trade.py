# -*- coding:utf-8 -*-
# !/usr/bin/env python
import logging
import time

from trade.hot_coin_api import HotCoin
from utils.config_loader import config
from utils.remind_func import remind_tg

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
                logger.info(f'{print_prefix} 买单 {round(float(start_price) - i * float(price_step), config.price_decimal_num)} {round(float(push_first_amount) + i * float(up_amount), config.vol_decimal_num)}')
                hot_coin.buy(round(float(start_price) - i * float(price_step), config.price_decimal_num), round(float(push_first_amount) + i * float(up_amount), 4))
                remind_tg(config.ALERT_PRICE_TG_CHAT, f'#{config.SYMBOL_NAME} \n'
                                                      f'发起批量挂单\n'
                                                      f'方向：买单\n'
                                                      f'价格：{round(float(start_price) - i * float(price_step), config.price_decimal_num)}\n'
                                                      f'数量：{round(float(push_first_amount) + i * float(up_amount), config.vol_decimal_num)}\n')
            else:
                if not config.ALERT_PRICE_MIN < float(start_price) + i * float(price_step) < config.ALERT_PRICE_MAX:
                    logger.warning(f'{print_prefix} 价格超出预警范围')
                    break
                logger.info(f'{print_prefix} 卖单 {round(float(start_price) + i * float(price_step), config.price_decimal_num)} {round(float(push_first_amount) + i * float(up_amount), config.vol_decimal_num)}')
                hot_coin.sell(round(float(start_price) + i * float(price_step), config.price_decimal_num), round(float(push_first_amount) + i * float(up_amount), config.vol_decimal_num))
                remind_tg(config.ALERT_PRICE_TG_CHAT, f'#{config.SYMBOL_NAME} \n'
                                                      f'发起批量挂单\n'
                                                      f'方向：卖单\n'
                                                      f'价格：{round(float(start_price) + i * float(price_step), config.price_decimal_num)}\n'
                                                      f'数量：{round(float(push_first_amount) + i * float(up_amount), config.vol_decimal_num)}\n')
            time.sleep(float(time_interval))
    except Exception as e:
        logger.error(f'{print_prefix} 发送错误')
        logger.exception(e)
