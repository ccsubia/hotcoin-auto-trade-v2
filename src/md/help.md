命令格式：/<命令名称>@<机器人user_name> <参数1>, <参数2>... 

> 参数之间用英文逗号隔开，命令与参数之间空格隔开，@不隔开，在群组中使用命令需带上@机器人user_name, 在与机器人私聊中无需加

> 如果直接修改config文件，需发送 `/reload_config` 命令到机器人刷新配置，否则会出现信息读取错误

> 对配置项修改的命令需得到机器人成功的回应，才可确认为设置成功

机器人设置了管理员访问禁止会进行写入影响的命令

- `/id` 获取自身id
- `/chat_id` 获取所在Chat ID
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