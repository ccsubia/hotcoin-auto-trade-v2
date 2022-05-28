# -*- coding:utf-8 -*-
# !/usr/bin/env python
import logging
import random
import time
from decimal import *

from utils.config_loader import config
from utils.remind_func import remind_tg

logger = logging.getLogger(__name__)


async def fill_depth(hot_coin, websocket):
    print_prefix = '[Fill Depth]'
    logger.info(print_prefix)
    self_cnt = 0
    try:
        while True:
            print_prefix = f'[Fill Depth: {self_cnt}]'
            config.load_config()

            # Check fill_depth_on
            if not config.fill_depth_on:
                logger.warning('fill_depth 关闭, 10秒后重试')
                self_cnt = 0
                time.sleep(10)
                continue

            # Get Depth
            self_coin_depth_data = hot_coin.get_depth()
            # logger.info(self_coin_depth_data)

            sellprice, buyprice = [], []
            if 'data' in self_coin_depth_data and 'depth' in self_coin_depth_data['data']:
                depth_data = self_coin_depth_data['data']['depth']
                if ('asks' in depth_data) and ('bids' in depth_data):
                    for order in depth_data['asks']:
                        sellprice.append(round(Decimal(order[0]), config.price_decimal_num))
                    for order in depth_data['bids']:
                        buyprice.append(round(Decimal(order[0]), config.price_decimal_num))
            else:
                logger.warning(f'{print_prefix} 深度获取失败')
                continue
            trade_all_list = []
            self_coin_b1_price = Decimal(round(buyprice[0], config.price_decimal_num))
            price_step = round(Decimal(0.1) ** config.price_decimal_num, config.price_decimal_num)
            for i in range(20):
                fill_sell_price = self_coin_b1_price + price_step * (i + 1)
                push_sell_price = round(fill_sell_price, config.price_decimal_num)
                push_sell_amount = round(random.uniform(config.fill_depth_random_amount_min,
                                                        config.fill_depth_random_amount_max), config.vol_decimal_num)
                if fill_sell_price not in sellprice:
                    trade_all_list.append({'price': push_sell_price, 'amount': push_sell_amount, 'trade_type': 0})

                fill_buy_price = self_coin_b1_price - price_step * (i + 1)
                push_buy_price = round(fill_buy_price, config.price_decimal_num)
                push_buy_amount = round(random.uniform(config.fill_depth_random_amount_min,
                                                       config.fill_depth_random_amount_max), config.vol_decimal_num)
                if fill_buy_price not in buyprice:
                    trade_all_list.append({'price': push_buy_price, 'amount': push_buy_amount, 'trade_type': 1})

            # 校验限制
            check_error_flag = False
            for item in trade_all_list:
                if not config.ALERT_PRICE_MAX > item["price"] > config.ALERT_PRICE_MIN:
                    logger.warning(f'{print_prefix}交易价格超出预警区间, 价格: {item["price"]}')
                    remind_tg(config.ALERT_PRICE_TG_CHAT, f'{print_prefix}交易价格超出预警区间, 价格: {item["price"]}')
                    check_error_flag = True
                    break
            if check_error_flag:
                self_cnt = 0
                time.sleep(30)
                continue

            # 发送交易
            for item in trade_all_list:
                logger.info(
                    f'{print_prefix} 下单方向:{item["trade_type"]}, 价格:{item["price"]}, 下单量:{item["amount"]}')
                result = hot_coin.trade(item["price"], item["amount"], item["trade_type"])
                resultId = result['data']['ID']
                logger.info(f'{print_prefix} 下单成功， ID：{resultId}')
            # Sleep
            logger.info(f'{print_prefix} 交易完成, {config.fill_depth_interval}秒后重新进入')
            time.sleep(config.fill_depth_interval)
            self_cnt += 1

    except Exception as e:
        logger.error(f'{print_prefix}: 未知错误')
        logger.exception(e)
        time.sleep(1)
