# -*- coding:utf-8 -*-
# !/usr/bin/env python
import logging
import random
import time
from decimal import *

from utils.config_loader import config
from utils.remind_func import remind_tg

logger = logging.getLogger(__name__)


async def jump_depth(hot_coin, websocket):
    print_prefix = '[Jump Depth]'
    logger.info(print_prefix)
    self_cnt = 0
    try:
        while True:
            print_prefix = f'[Jump Depth: {self_cnt}]'
            config.load_config()

            # Check jump_depth_on
            if not config.jump_depth_on:
                logger.warning('jump_depth 关闭, 30秒后重试')
                self_cnt = 0
                time.sleep(30)
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
            for i in range(int(config.jump_depth_count)):
                r = random.randint(3, 20)
                fill_sell_price = self_coin_b1_price + price_step * r
                push_sell_price = round(fill_sell_price, config.price_decimal_num)
                push_sell_amount = round(random.uniform(config.jump_depth_vol_min,
                                                        config.jump_depth_vol_max), config.vol_decimal_num)

                trade_all_list.append({'price': push_sell_price, 'amount': push_sell_amount, 'trade_type': 0})

                fill_buy_price = self_coin_b1_price - price_step * r
                push_buy_price = round(fill_buy_price, config.price_decimal_num)
                push_buy_amount = round(random.uniform(config.jump_depth_vol_min,
                                                       config.jump_depth_vol_max), config.vol_decimal_num)

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

            pending_cancel_order_list = []
            # 发送交易
            for item in trade_all_list:
                logger.info(
                    f'{print_prefix} 下单方向:{item["trade_type"]}, 价格:{item["price"]}, 下单量:{item["amount"]}')
                result = hot_coin.trade(item["price"], item["amount"], item["trade_type"])
                resultId = result['data']['ID']
                logger.info(f'{print_prefix} 下单成功， ID：{resultId}')
                pending_cancel_order_list.append(resultId)
            # 等待取消
            logger.info(f'{print_prefix} 下单完成, {config.jump_depth_cancel_interval}秒后取消挂单')
            time.sleep(config.jump_depth_cancel_interval)
            for item in pending_cancel_order_list:
                logger.info(f'{print_prefix} 撤销订单, ID => {item}')
                cancel_result = hot_coin.cancel_order(item)
                logger.debug(f'{print_prefix} 撤销结果 {cancel_result}')
            # Sleep
            logger.info(f'{print_prefix} 撤销完成, {config.jump_depth_interval}秒后重新进入')
            time.sleep(config.jump_depth_interval)
            self_cnt += 1

    except Exception as e:
        logger.error(f'{print_prefix}: 未知错误, 睡眠{config.jump_depth_interval}秒')
        logger.exception(e)
        time.sleep(config.jump_depth_interval)
