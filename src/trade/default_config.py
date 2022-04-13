# encoding=utf-8

config = {
    #################################
    # 交易调节参数设置
    # 'key': '',
    # 'secret': '',
    # 下单配置
    'price_decimal_num': 4,  # 下单价格小数点位数
    'volumn_decimal_num': 1,  # 下单数量小数点位数
    # 撤单配置
    'cancel_adjustable_time': 30,  # 撤单频率，秒
    # self交易配置
    'self_tradeFrequence': 10,  # self交易频率，秒
    'self_tradeMin': 20,  # self交易数量最小值
    'self_tradeMax': 50,  # self交易数量最大值
    # cross交易配置
    'cross_tradeFrequence': 10,  # cross交易频率，秒
    'cross_tradeMin': 111,  # cross交易数量最小值
    'cross_tradeMax': 113,  # cross交易数量最大值
    'cross_depth': 10,  # cross交易深度
    'cross_trade_price_max': 0,  # cross交易价格的最大值，为0表示不设置
    'cross_trade_price_min': 0,  # cross交易价格的最小值，为0表示不设置
    #################################
    # 波动交易配置
    # 自动配置
    'wave_trade_auto_on': False,  # 是否启用自动波动交易, True or False
    'wave_trade_auto_min_percentage': -0.01,  # 自动波动交易:波动下限
    'wave_trade_auto_max_percentage': 0.01,  # 自动波动交易:波动上限
    'wave_trade_auto_min_action_num': 1,  # 自动波动交易:波动次数下限'
    'wave_trade_auto_max_action_num': 3,  # 自动波动交易:波动次数上限'
    # 手动配置
    'wave_trade_manual_on': False,  # 是否启用手动配置波动交易, True or False
    'wave_trade_time_format': '%Y-%m-%d/%H:%M:%S',  # 启动时间点时间格式
    'wave_trade_repeat_evenyday': True,  # wave波动交易：是否每天执行手动配置，如果是，则程序忽略启动时间点配置的年月日，年月日可配置为任意时间
    'wave_trade_start_times': ['2022-04-05/20:14:00', '2022-04-05/22:20:00'],  # wave波动交易：启动时间点
    'wave_trade_percentages': [-0.002, 0.002],  # wave波动交易：波动值，0.01为1%
    'wave_trade_duration_times': [1, 1],  # wave波动交易：持续时间（单位分钟）
    'wave_trade_action_nums': [2, 2],  # wave波动交易：分n次完成波动交易
    #################################
    # 以下是接口相关参数配置，一般不用修改
    'symbol': 'apg_usdt',  # 币种
    'depth_param': '{"sub": "market.apg_usdt.trade.depth"}',  # 获取深度信息的参数
    'web_addr': 'wss://wss.hotcoinfin.com/trade/multiple',  # websocket接口地址
    #################################
    # 以下是程序运行配置，一般不用修改
    'cancel_data_dir': './data/cancel_data',  # 撤单订单数据
    'trade_data_dir': './data/trade_data',  # 成交订单数据
    'cancel_report_dir': './reports/cancel',  # 撤单订单统计报告输出路径
    'trade_report_dir': './reports/trade',  # 成交订单统计报告输出路径
    'save_file_num': 1000,
    'report_hour': 16,
    'debug': False,
}
