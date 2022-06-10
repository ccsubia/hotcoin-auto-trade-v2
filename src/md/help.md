命令格式：/<命令名称>@<机器人user_name> <参数1>, <参数2>... 

> 参数之间用英文逗号隔开，命令与参数之间空格隔开，@不隔开，在群组中使用命令需带上@机器人user_name, 在与机器人私聊中无需加

> 如果直接修改config文件，需发送 `/reload_config` 命令到机器人刷新配置，否则会出现信息读取错误

> 对配置项修改的命令需得到机器人成功的回应，才可确认为设置成功

机器人设置了管理员访问禁止会进行写入影响的命令

- `/id` 获取自身id
- `/chat_id` 获取所在Chat ID
- `/all_config_show` 展示全部配置
- `/add_admin`  添加管理员
    - 参数1 → 添加的管理员ID
- `/rm_admin`  添加管理员
    - 参数1 → 移除的管理员ID
- `/admin_list` 查看管理员列表ID
- `/alert_tg_on`   开启TG预警
- `/alert_tg_off` 关闭 TG预警
- `/alert_server_jiang_on`开启Server酱预警
- `/alert_server_jiang_off` 关闭Server酱预警
- `/alert_config_show` 显示当前预警配置
- `/set_alert_price_min` 设置最小超出触法价格
    - 参数1 → 价格
- `/set_alert_price_max` 设置最大超出触发价格
    - 参数1 → 价格
- `/set_alert_price_interval_minute` 设置预警间隔时间
    - 参数1 → 预警间隔时间，单位分钟
- `/set_alert_price_tg_chat` 设置预警发送对话
    - 参数1 → 预警发送到TG对话ID
- `set_alert_usdt_balance_over` 设置预警USDT减少数量
- `/fork_trade_on`  开启对标交易
- `/fork_trade_off` 关闭对标交易
- `/fork_trade_config_show` 查看当前对标交易配置
- `/set_fork_trade_amount_max` 设置买卖1最大交易数量
    - 参数1 → 买卖1最大交易数量
- `/set_fork_trade_random_amount_min` 设置买卖2-3随机最低交易量
    - 参数1 → 买卖2-3随机最低交易量
- `/set_fork_trade_random_amount_max` 设置买卖2-3随机最高交易量
    - 参数1 → 买卖2-3随机最高交易量
- `/auto_fork_trade_config_on`  开启自动调整对标交易配置
- `/auto_fork_trade_config_off` 关闭自动调整对标交易配置
- `/set_fork_random_amount_min_min` 自动调整复刻盘口最小交易量区间最小值
- `/set_fork_random_amount_min_max` 自动调整复刻盘口最小交易量区间最大值
- `/set_fork_random_amount_max_min` 自动调整复刻盘口最大交易量区间最小值
- `/set_fork_random_amount_max_max` 自动调整复刻盘口最大交易量区间最大值
- `/set_fork_trade_interval` 设置fork交易间隔(秒)
- `/set_fork_symbol` 设置对标代币
- `/batch_push_trade_on`开启批量挂单
- `/batch_push_trade_off`关闭批量挂单
- `/pending_batch_push_trade_show`查看当前待执行批量挂单任务
- `/add_batch_push_trade` 添加批量挂单任务
    - 参数1 → 买卖方向（1⇒买，0⇒ 卖）
    - 参数2 → 挂单数
    - 参数3 → 开始价格
    - 参数4 → 价格间隔（买单每单从开始价格递减，卖单反之递增）
    - 参数5 → 开始单量
    - 参数6 → 单量增量
    - 参数7 → 每单挂单时间间隔
- `/fast_add_batch_push_trade` 快速添加批量挂单
  - 无参数
- `/confirm_add_batch_push_trade` 确认执行批量挂单
- `/reset_pending_batch_push_trade` 清除当前待执行批量挂单任务
- `/set_alert_vol_count_minute` 设置交易量检测的时间段, 单位分钟
    - 参数1 → 时间段,单位分钟
- `/set_alert_vol_min` 设置时间段内需满足的最小交易量
    - 参数1 → 需满足的最小交易量
- `/auto_batch_push_trade_show` 达到最大价格自动交易配置
- `/set_auto_batch_push_trade` 达到最大价格预设自动交易
    - 参数1 → 买卖方向（1⇒买，0⇒ 卖）
    - 参数2 → 挂单数
    - 参数3 → 开始价格
    - 参数4 → 价格间隔（买单每单从开始价格递减，卖单反之递增）
    - 参数5 → 开始单量
    - 参数6 → 单量增量
    - 参数7 → 每单挂单时间间隔
- `/reset_auto_batch_push_trade` 清除达到最大价格自动交易预设
- `/auto_batch_push_trade_show2` 达到最小价格自动交易配置
- `/set_auto_batch_push_trade2` 达到最小价格预设自动交易
    - 参数1 → 买卖方向（1⇒买，0⇒ 卖）
    - 参数2 → 挂单数
    - 参数3 → 开始价格
    - 参数4 → 价格间隔（买单每单从开始价格递减，卖单反之递增）
    - 参数5 → 开始单量
    - 参数6 → 单量增量
    - 参数7 → 每单挂单时间间隔
- `/reset_auto_batch_push_trade2` 清除达到最小价格自动交易预设
- `/default_batch_push_trade_show` 查看默认批量挂单配置
- `/set_default_batch_push_trade` 设置默认批量挂单配置
    - 参数1 → 买卖方向（1⇒买，0⇒ 卖）
    - 参数2 → 挂单数
    - 参数3 → 开始价格
    - 参数4 → 价格间隔（买单每单从开始价格递减，卖单反之递增）
    - 参数5 → 开始单量
    - 参数6 → 单量增量
    - 参数7 → 每单挂单时间间隔

- `/self_trade_config_show` 查看Self 交易配置
- `/set_self_trade_interval` 设置Self交易时间间隔(秒)
- `/set_self_tradeMin`设置Self交易最小交易量
- `/set_self_tradeMax`设置Self交易最大交易量

- `/cross_trade_config_show`查看Cross 交易配置
- `/set_cross_trade_interval` 设置Cross 交易时间间隔(秒)
- `/set_cross_tradeMin`设置Cross 交易最小交易量
- `/set_cross_tradeMax`设置Cross 交易最大交易量
- `/set_cross_trade_price_min`设置Cross 交易最小价格
- `/set_cross_trade_price_max`设置Cross 交易最大价格
- `/set_cross_depth`设置Cross 交易深度

- `/cancel_config_show`查看撤单配置
- `/set_cancel_adjustable_time`设置撤单时间间隔(秒)
- `/set_cancel_before_order_minutes` 设置撤销委托单大于距当前分钟数

- `/decimal_config_show` 查看精度配置
- `/set_price_decimal_num` 设置价格精度
- `/set_vol_decimal_num` 设置交易量精度