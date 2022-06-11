# -*- coding:utf-8 -*-
import asyncio
import configparser
import datetime
import logging
import math
import multiprocessing
import os
import time

import websockets
from apscheduler.schedulers.blocking import BlockingScheduler

from tg.bot import main as tg_bot
from trade import hot_coin_func_trade, utils
from trade.alert_price import alert_price
from trade.default_config import config
from trade.fill_depth import fill_depth
from trade.fork_trade import fork_trade
from trade.hot_coin_api import HotCoin
from trade.jump_depth import jump_depth
from utils.account_info import accountClass
from utils.config_loader import config as new_config
from utils.logger_init import init_logger
from utils.remind_func import remind_tg

raw_config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
logger = logging.getLogger(__name__)

init_logger(__file__)


def cancel_pool(hot_coin):
    while True:
        try:
            hot_coin_func_trade.adjustable_cancel(hot_coin)
        except Exception as e:
            logger.exception(e)
        time.sleep(2)


def save_trades_pool(hot_coin):
    while True:
        try:
            hot_coin_func_trade.save_trades(hot_coin, config['trade_data_dir'])
        except Exception as e:
            logger.exception(e)
        time.sleep(60 * 10)  # 每10分钟获取最新订单信息并存储


def print_trade_pool():
    while True:
        try:
            end_day = utils.get_now_time_str(time_format='%Y%m%d')
            end_time = f'{end_day}{config["report_hour"]:02d}0000'
            if utils.get_now_time_str() < end_time:
                if config['debug']:
                    time.sleep(10)
                else:
                    time.sleep(60 * 60)  # 每60分钟尝试输出报告
                continue
            start_time = f'{utils.cal_date(end_day, -1)}{config["report_hour"]:02d}0000'
            hot_coin_func_trade.print_trade_report(
                input_dir=config['trade_data_dir'],
                output_dir=config['trade_report_dir'],
                start_time=start_time, end_time=end_time)
        except Exception as e:
            logger.exception(e)
        if config['debug']:
            time.sleep(10)
        else:
            time.sleep(60 * 60)


def print_cancel_pool():
    while True:
        try:
            end_day = utils.get_now_time_str(time_format='%Y%m%d')
            end_time = f'{end_day}{config["report_hour"]:02d}0000'
            if utils.get_now_time_str() < end_time:
                if config['debug']:
                    time.sleep(10)
                else:
                    time.sleep(60 * 60)  # 每60分钟尝试输出报告
                continue
            start_time = f'{utils.cal_date(end_day, -1)}{config["report_hour"]:02d}0000'
            hot_coin_func_trade.print_cancel_report(
                input_dir=config['cancel_data_dir'],
                output_dir=config['cancel_report_dir'],
                start_time=start_time, end_time=end_time)
        except Exception as e:
            logger.exception(e)
        if config['debug']:
            time.sleep(10)
        else:
            time.sleep(60 * 60)


def wave_trade_pool(hot_coin):
    while True:
        try:
            # 自动波动交易
            if config['wave_trade_auto_on']:
                start_day = utils.get_now_time_str(time_format='%Y%m%d')
                # generate auto config
                wave_num = utils.random_num(
                    min_val=config['wave_trade_auto_min_action_num'],
                    max_val=config['wave_trade_auto_max_action_num'] + 1,
                    num=1,
                    sigma=1)[0]
                now_time = utils.get_now_time_str(time_format='%Y%m%d%H%M%S')
                end_time = f"{start_day}235959"
                wave_times = utils.random_num(
                    min_val=int(now_time),
                    max_val=int(end_time),
                    num=int(wave_num),
                    sigma=1)
                wave_percentages = utils.random_num(
                    min_val=config['wave_trade_auto_min_percentage'],
                    max_val=config['wave_trade_auto_max_percentage'],
                    num=int(wave_num),
                    sigma=10000)
                while True:
                    now_day = utils.get_now_time_str(time_format='%Y%m%d')
                    if now_day > start_day:
                        break
                    now_time = utils.get_now_time_str(time_format='%Y%m%d%H%M%S')
                    for index, start_time in enumerate(wave_times):
                        print(start_time)
                        print(now_time)
                        if int(now_time) > start_time and int(now_time) - int(start_time) < 60:
                            # time check pass
                            print('ok')
                            wave_percentage = wave_percentages[index]
                            duration_time = utils.random_num(1, 60)
                            action_num = utils.random_num(1, 3)
                            hot_coin_func_trade.target_trade_allocation(hot_coin, wave_percentage, duration_time,
                                                                        action_num)
                            time.sleep(61)
                    time.sleep(10)
            elif config['wave_trade_manual_on']:
                # 手动配置的波动交易
                assert len(config['wave_trade_start_times']) == len(config['wave_trade_percentages'])
                assert len(config['wave_trade_start_times']) == len(config['wave_trade_duration_times'])
                assert len(config['wave_trade_start_times']) == len(config['wave_trade_action_nums'])
                now_time = utils.get_now_time_str(time_format='%Y%m%d%H%M%S')
                for index, start_time in enumerate(config['wave_trade_start_times']):
                    start_time = utils.time_format_change(start_time, config['wave_trade_time_format'])
                    if config['wave_trade_repeat_evenyday']:
                        start_time = f"{utils.get_now_time_str(time_format='%Y%m%d')}{start_time[-6:]}"
                    print(start_time)
                    print(now_time)
                    if now_time > start_time and int(now_time) - int(start_time) < 60:
                        # time check pass
                        # print('ok')
                        wave_percentage = config['wave_trade_percentages'][index]
                        duration_time = config['wave_trade_duration_times'][index]
                        action_num = config['wave_trade_action_nums'][index]
                        hot_coin_func_trade.target_trade_allocation(hot_coin, wave_percentage, duration_time,
                                                                    action_num)
                        time.sleep(61)
        except Exception as e:
            logger.exception(e)
        time.sleep(10)


# async func
def func(hot_coin, target_func):
    while True:
        try:
            logging.info("Start main func...")

            async def main_logic():
                async with websockets.connect(new_config.WEBSOCKETS_API, ping_interval=None) as websocket:
                    await target_func(hot_coin, websocket)

            asyncio.get_event_loop().run_until_complete(main_logic())
        except Exception as e:
            logger.exception(e)
            logging.warning("Main func failed, restart")


def run_sched():
    sched = BlockingScheduler(timezone="Asia/Shanghai")

    # 输出时间
    # @sched.scheduled_job('cron', minute=0, hour='*/8')
    # # @sched.scheduled_job('interval', seconds=5)
    # def job():
    #     gen_volume_report()
    #     gen_assets_report()
    #     gen_analyze_report()

    @sched.scheduled_job('interval', seconds=60)
    def check_status():
        print_prefix = f'[Status Check]'
        try:
            new_config.load_config()
            logger.info(f'{print_prefix}')
            new_hot_coin = HotCoin(symbol=new_config.SYMBOL)
            ticker_data = new_hot_coin.get_ticker(step=60)
            if 'data' in ticker_data and 'time' in ticker_data:
                current_time = float(ticker_data['time'])
                ticker_data = ticker_data['data'][::-1]
                minutes_vol = 0
                for item in ticker_data:
                    if float(item[0]) < current_time - (new_config.alert_vol_count_minute * 60 * 1000):
                        break
                    minutes_vol += float(item[5])

                if minutes_vol < new_config.alert_vol_min:
                    logger.warning(f'{print_prefix} 交易量异常，{new_config.alert_vol_count_minute}分钟内交易 {minutes_vol}，'
                                   f'小于设定最小值{new_config.alert_vol_min}')
                    remind_tg(new_config.ALERT_PRICE_TG_CHAT,
                              f'#{new_config.SYMBOL_NAME} \n'
                              f'检测到最近{new_config.alert_vol_count_minute}分钟交易量低于预警交易量{new_config.alert_vol_min}\n'
                              f'交易量总计{round(minutes_vol, 4)}')
                else:
                    logger.info(f'{print_prefix} 交易量正常，{new_config.alert_vol_count_minute}分钟内交易 {minutes_vol}，'
                                f'大于设定最小值{new_config.alert_vol_min}')
            else:
                logger.warning(f'{print_prefix} 交易量获取失败 {ticker_data}')
                remind_tg(new_config.ALERT_PRICE_TG_CHAT, '交易量获取失败，请检查IP是否被封禁')
        except Exception as e:
            logger.exception(e)
            remind_tg(new_config.ALERT_PRICE_TG_CHAT, f'{print_prefix} 遇到未知错误: ' + str(e))

    @sched.scheduled_job('interval', seconds=60)
    def check_account_balance_status():
        print_prefix = f'[Account Balance Check]'
        try:
            new_config.load_config()
            logger.info(f'{print_prefix}')
            new_hot_coin = HotCoin(symbol=new_config.SYMBOL)
            new_hot_coin.auth(key=new_config.ACCESS_KEY, secret=new_config.SECRET_KEY)
            account_info_data = new_hot_coin.get_account_info()
            if 'data' in account_info_data and 'wallet' in account_info_data['data']:
                bot_usdt_balance = 0
                bot_usdt_free_balance = 0
                for item in account_info_data['data']['wallet']:
                    if item['symbol'] == 'USDT':
                        bot_usdt_balance = float(item['total']) + float(item['frozen'])
                        bot_usdt_free_balance = float(item['total'])
                        logger.info(f'{print_prefix} 当前Bot账户USDT余额：{bot_usdt_balance}')
                        break
                if datetime.datetime.now().minute == 0 or accountClass.BOT_USDT_BALANCE == 0:
                    accountClass.BOT_USDT_BALANCE = bot_usdt_balance
                    remind_tg(new_config.REPORT_TG_CHAT, f'#报告\n'
                                                         f'[Bot账户] 当前USDT余额：{bot_usdt_balance}\n'
                                                         f'可用余额：{bot_usdt_free_balance}')
                else:
                    sub_balance = accountClass.BOT_USDT_BALANCE - bot_usdt_balance
                    if sub_balance > new_config.alert_usdt_balance_over_amount:
                        logger.warning(f'{print_prefix} [Bot账户] USDT余额异常\n'
                                       f'当前USDT余额：{bot_usdt_balance}\n'
                                       f'可用余额：{bot_usdt_free_balance}')
                        remind_tg(new_config.ALERT_PRICE_TG_CHAT, f'#预警\n'
                                                                  f'[Bot账户] USDT余额异常\n'
                                                                  f'当前USDT余额：{bot_usdt_balance}\n'
                                                                  f'可用余额：{bot_usdt_free_balance}\n'
                                                                  f'总余额减少：{sub_balance}')
            else:
                logger.warning(f'{print_prefix} 账户信息获取失败 {account_info_data}')
                remind_tg(new_config.ALERT_PRICE_TG_CHAT, '账户信息获取失败，请检查IP是否被封禁')

            for index in range(len(new_config.OTHER_ACCESS_KEYS)):
                new_hot_coin.auth(key=new_config.OTHER_ACCESS_KEYS[index], secret=new_config.OTHER_SECRET_KEYS[index])
                account_info_data = new_hot_coin.get_account_info()
                if 'data' in account_info_data and 'wallet' in account_info_data['data']:
                    usdt_balance = 0
                    usdt_free_balance = 0
                    for item in account_info_data['data']['wallet']:
                        if item['symbol'] == 'USDT':
                            usdt_balance = float(item['total']) + float(item['frozen'])
                            usdt_free_balance = float(item['total'])
                            logger.info(f'{print_prefix} 当前人工账户{index + 1} USDT余额：{usdt_balance}')
                            break
                    if len(accountClass.OTHER_ACCOUNT_USDT_BALANCE) == index:
                        accountClass.OTHER_ACCOUNT_USDT_BALANCE.append(0)
                    if datetime.datetime.now().minute == 0 or accountClass.OTHER_ACCOUNT_USDT_BALANCE[index] == 0:
                        accountClass.OTHER_ACCOUNT_USDT_BALANCE[index] = usdt_balance
                        remind_tg(new_config.REPORT_TG_CHAT, f'#报告\n'
                                                             f'[人工账户{index + 1}] 当前USDT余额：{usdt_balance}\n'
                                                             f'可用余额：{usdt_free_balance}')
                    else:
                        sub_balance = accountClass.OTHER_ACCOUNT_USDT_BALANCE[index] - usdt_balance
                        if sub_balance > new_config.alert_usdt_balance_over_amount:
                            logger.warning(f'{print_prefix} [人工账户{index + 1}] USDT余额异常\n'
                                           f'当前USDT余额：{usdt_balance}\n'
                                           f'可用余额：{usdt_free_balance}')
                            remind_tg(new_config.ALERT_PRICE_TG_CHAT, f'#预警\n'
                                                                      f'[人工账户{index + 1}] USDT余额异常\n'
                                                                      f'当前USDT余额：{usdt_balance}\n'
                                                                      f'可用余额：{usdt_free_balance}\n'
                                                                      f'总余额减少：{sub_balance}')
                else:
                    logger.warning(f'{print_prefix} 账户信息获取失败 {account_info_data}')
                    remind_tg(new_config.ALERT_PRICE_TG_CHAT, '账户信息获取失败，请检查IP是否被封禁')
        except Exception as e:
            logger.exception(e)
            remind_tg(new_config.ALERT_PRICE_TG_CHAT, f'{print_prefix} 遇到未知错误: ' + str(e))

    @sched.scheduled_job('interval', seconds=60)
    def cancelOldOrder():
        print_prefix = f'[cancelOldOrder]'
        try:
            new_config.load_cancel_config()
            # print(new_config.cancel_before_order_minutes)
            logger.info(f'{print_prefix}')
            new_hot_coin = HotCoin(symbol=new_config.SYMBOL)
            new_hot_coin.auth(key=new_config.ACCESS_KEY, secret=new_config.SECRET_KEY)
            page = 1
            toCancelOrders = []
            while True:
                logger.debug(f'{print_prefix} Get Page {page}')
                currentOrderData = new_hot_coin.get_open_order(page)
                if 'data' in currentOrderData and 'entrutsCur' in currentOrderData['data']:
                    if len(currentOrderData['data']['entrutsCur']) > 0:
                        nowTimestamp = currentOrderData['time'] / 1000
                        logger.debug(nowTimestamp)
                        for item in currentOrderData['data']['entrutsCur']:
                            orderTimestamp = datetime.datetime.strptime(item['time'], '%Y-%m-%d %H:%M:%S').timestamp()
                            if orderTimestamp < nowTimestamp - new_config.cancel_before_order_minutes * 60:
                                toCancelOrders.append(item['id'])
                        page += 1
                    else:
                        logger.debug(toCancelOrders)
                        if len(toCancelOrders) > 0:
                            for n in range(math.ceil(len(toCancelOrders) / 10)):
                                logger.info(f'{print_prefix} 批量撤单，IDS => {toCancelOrders[n * 10: (n+1) * 10]}')
                                postStr = str(toCancelOrders[n * 10: (n+1) * 10]).replace('[', '').replace(']', '').replace(' ', '')
                                logger.debug(postStr)
                                logger.info(new_hot_coin.cancel_order_batch(postStr))
                        break
                else:
                    logger.warning(f'{print_prefix} 委托单数据获取错误')
                    break
        except Exception as e:
            logger.exception(e)
            remind_tg(new_config.ALERT_PRICE_TG_CHAT, f'{print_prefix} 遇到未知错误: ' + str(e))

    @sched.scheduled_job('interval', seconds=300)
    def auto_fork_config():
        print_prefix = f'[Auto Fork Config]'
        try:
            new_config.load_config()
            logger.info(f'{print_prefix}')
            if not new_config.auto_fork_trade_config_on:
                logger.info(f'{print_prefix} 未开启')
                return
            new_hot_coin = HotCoin(symbol=new_config.SYMBOL)
            ticker_data = new_hot_coin.get_ticker(step=300)
            if 'data' in ticker_data and 'time' in ticker_data:
                current_time = float(ticker_data['time'])
                ticker_data = ticker_data['data'][::-1]
                # logger.debug(ticker_data)
                skip_vol = 0
                skip_time = math.fmod(current_time, new_config.target_vol_interval_minutes * 60 * 1000)
                for item in ticker_data:
                    if float(item[0]) < current_time - skip_time:
                        break
                    skip_vol += float(item[5])
                if skip_vol <= 0:
                    logger.info(f'{print_prefix} 已产生交易量为0')
                    return False
                logger.info(f'{print_prefix} 已度过时间 => {skip_time / 1000 / 60} 分钟')
                logger.info(f'{print_prefix} 已产生交易量 => {skip_vol}')
                time_scale = new_config.target_vol_interval_minutes * 60 * 1000 / skip_time
                logger.info(f'{print_prefix} 预计交易量 => {skip_vol * time_scale}')
                logger.info(f'{print_prefix} 目标交易量 => {new_config.target_vol}')
                vol_scale = new_config.target_vol / (skip_vol * time_scale)
                logger.info(f'{print_prefix} vol_scale => {vol_scale}')

                logger.info(f'{print_prefix} fork_trade_random_amount_min => {new_config.fork_trade_random_amount_min}')
                logger.info(f'{print_prefix} fork_trade_random_amount_max => {new_config.fork_trade_random_amount_max}')

                new_config.fork_trade_random_amount_min = max(new_config.fork_trade_random_amount_min_min,
                                                              vol_scale * new_config.fork_trade_random_amount_min)
                new_config.fork_trade_random_amount_min = min(new_config.fork_trade_random_amount_min_max,
                                                              new_config.fork_trade_random_amount_min)

                new_config.fork_trade_random_amount_max = max(new_config.fork_trade_random_amount_max_min,
                                                              vol_scale * new_config.fork_trade_random_amount_max)
                new_config.fork_trade_random_amount_max = min(new_config.fork_trade_random_amount_max_max,
                                                              new_config.fork_trade_random_amount_max)

                raw_config = configparser.ConfigParser()
                raw_config.read(raw_config_path, encoding='utf-8')
                raw_config['Trade']['fork_trade_random_amount_min'] = str(new_config.fork_trade_random_amount_min)
                raw_config['Trade']['fork_trade_random_amount_max'] = str(new_config.fork_trade_random_amount_max)
                with open(raw_config_path, 'w') as configfile:
                    raw_config.write(configfile)
                logger.info(f'{print_prefix} new fork_trade_random_amount_min => {new_config.fork_trade_random_amount_min}')
                logger.info(f'{print_prefix} new fork_trade_random_amount_max => {new_config.fork_trade_random_amount_max}')
            else:
                logger.warning(f'{print_prefix} 交易量获取失败 {ticker_data}')
                remind_tg(new_config.ALERT_PRICE_TG_CHAT, f'{print_prefix} 交易量获取失败，请检查IP是否被封禁')
        except Exception as e:
            logger.exception(e)
            remind_tg(new_config.ALERT_PRICE_TG_CHAT, f'{print_prefix} 遇到未知错误: ' + str(e))

    sched.start()


# BlockingScheduler
# sched.add_job(job, 'cron', minutes='*/2')

new_config.load_all_config()

if __name__ == '__main__':
    hot_coin = HotCoin(symbol=new_config.SYMBOL)
    hot_coin.auth(key=new_config.ACCESS_KEY, secret=new_config.SECRET_KEY)
    multiprocessing.set_start_method('spawn')
    pool = multiprocessing.Pool(processes=13)
    pool.apply_async(func, (hot_coin, hot_coin_func_trade.self_trade,))
    pool.apply_async(func, (hot_coin, hot_coin_func_trade.cross_trade,))
    pool.apply_async(cancel_pool, (hot_coin,))
    pool.apply_async(save_trades_pool, (hot_coin,))
    pool.apply_async(print_trade_pool)
    pool.apply_async(print_cancel_pool)
    pool.apply_async(wave_trade_pool, (hot_coin,))
    # pool.apply_async(func, (hot_coin, period_trade.period_trade,))
    pool.apply_async(func, (hot_coin, alert_price,))
    pool.apply_async(func, (hot_coin, fork_trade,))
    pool.apply_async(func, (hot_coin, jump_depth,))
    pool.apply_async(func, (hot_coin, fill_depth,))
    pool.apply_async(tg_bot)
    pool.apply_async(run_sched)
    pool.close()
    pool.join()
