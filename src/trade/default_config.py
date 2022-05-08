# encoding=utf-8

config = {
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
    # 以下是程序运行配置，一般不用修改
    'cancel_data_dir': './data/cancel_data',  # 撤单订单数据
    'trade_data_dir': './data/trade_data',  # 成交订单数据
    'cancel_report_dir': './reports/cancel',  # 撤单订单统计报告输出路径
    'trade_report_dir': './reports/trade',  # 成交订单统计报告输出路径
    'save_file_num': 1000,
    'report_hour': 16,
    'debug': False,
}
