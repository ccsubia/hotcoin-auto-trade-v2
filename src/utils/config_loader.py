import configparser
import os
import logging
import sys

logger = logging.getLogger(__name__)


class _Config:
    def __init__(self):
        self._access_key = ''
        self._secret_key = ''
        self._other_access_keys = ''
        self._other_secret_keys = ''
        self._bot_token = ''
        self._bot_name = ''
        self._server_jiang_token = ''
        self._super_admin = ''
        self._symbol = ''
        self._symbol_name = ''
        self._http_api = ''
        self._websockets_api = ''
        self._admins = ''
        self._period_trade_on = False
        self._default_period_trade_amount_min = 0
        self._default_period_trade_amount_max = 0
        self._default_period_max_trade_amount = 0
        self._default_period_trade_interval_time = 10
        self._default_period_is_open = True

        self._alert_price_server_jiang_on = False
        self._alert_price_tg_on = False
        self._alert_price_tg_chat = 0
        self._alert_price_interval_minute = 0
        self._alert_price_min = 0
        self._alert_price_max = 0
        self._alert_vol_count_minute = 0
        self._alert_vol_min = 0
        self._alert_usdt_balance_over_amount = 0

        self._report_tg_chat = 0

        self._batch_push_trade_on = False
        self._auto_batch_push_trade_type = 0
        self._auto_batch_push_trade_push_count = 0
        self._auto_batch_push_trade_start_price = 0
        self._auto_batch_push_trade_price_step = 0
        self._auto_batch_push_trade_push_first_amount = 0
        self._auto_batch_push_trade_up_amount = 0
        self._auto_batch_push_trade_time_interval = 0
        self._auto_batch_push_trade_type2 = 0
        self._auto_batch_push_trade_push_count2 = 0
        self._auto_batch_push_trade_start_price2 = 0
        self._auto_batch_push_trade_price_step2 = 0
        self._auto_batch_push_trade_push_first_amount2 = 0
        self._auto_batch_push_trade_up_amount2 = 0
        self._auto_batch_push_trade_time_interval2 = 0

        self._fork_trade_on = False
        self._fork_trade_amount_max = 0
        self._fork_trade_random_amount_min = 0
        self._fork_trade_random_amount_max = 0
        self._fork_trade_interval = 0

        self._price_decimal_num = 8
        self._vol_decimal_num = 2

        self._self_trade_interval = 10
        self._self_trade_min = 0
        self._self_trade_max = 0

        self._cross_trade_interval = 10
        self._cross_trade_min = 0
        self._cross_trade_max = 1
        self._cross_depth = 10
        self._cross_trade_price_min = 0
        self._cross_trade_price_max = 0

        self._cancel_adjustable_time = 30

    def load_config(self):
        try:
            config_file = configparser.ConfigParser(allow_no_value=True)
            config_file.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'),
                             encoding='utf-8')
        except Exception as err:
            logger.warning("Can't open the config file: ", err)
            sys.exit(1)
        if not config_file.has_section('Secret'):
            logger.warning("Can't find Secret section in config.")
            sys.exit(1)
        config_secret = config_file['Secret']
        if not config_file.has_section('API'):
            logger.warning("Can't find API section in config.")
            sys.exit(1)
        config_api = config_file['API']
        if not config_file.has_section('Trade'):
            logger.warning("Can't find Trade section in config.")
            sys.exit(1)
        config_trade = config_file['Trade']
        if not config_file.has_section('Alert'):
            logger.warning("Can't find Alert section in config.")
            sys.exit(1)
        config_alert = config_file['Alert']
        config_report = config_file['Report']

        config_secret_keywords_str = [
            'access_key',
            'secret_key',
            'bot_token',
            'bot_name',
        ]
        config_secret_keywords_optional_str = [
            'other_access_keys',
            'other_secret_keys',
            'server_jiang_token',
        ]
        config_api_keywords_str = [
            'symbol',
            'symbol_name',
            'http_api',
            'websockets_api',
        ]
        config_trade_keywords_float = [
            'default_period_trade_amount_min',
            'default_period_trade_amount_max',
            'default_period_max_trade_amount',
            'default_period_trade_interval_time',
            'fork_trade_amount_max',
            'fork_trade_random_amount_min',
            'fork_trade_random_amount_max',
            'fork_trade_interval',
        ]
        config_trade_keywords_bool = [
            'period_trade_on',
            'default_period_is_open',
            'batch_push_trade_on',
            'fork_trade_on'
        ]

        config_auto_push_trade_keywords_float = [
            'auto_batch_push_trade_type',
            'auto_batch_push_trade_push_count',
            'auto_batch_push_trade_start_price',
            'auto_batch_push_trade_price_step',
            'auto_batch_push_trade_push_first_amount',
            'auto_batch_push_trade_up_amount',
            'auto_batch_push_trade_time_interval',
            'auto_batch_push_trade_type2',
            'auto_batch_push_trade_push_count2',
            'auto_batch_push_trade_start_price2',
            'auto_batch_push_trade_price_step2',
            'auto_batch_push_trade_push_first_amount2',
            'auto_batch_push_trade_up_amount2',
            'auto_batch_push_trade_time_interval2',
        ]

        self.get_config_from_section('str', config_secret_keywords_str, config_secret)
        self.get_config_from_section('str', config_secret_keywords_optional_str, config_secret, optional=True)
        self.get_config_from_section('str', config_api_keywords_str, config_api)

        self.get_config_from_section('str', ['super_admin'], config_file['Admin'])
        self.get_config_from_section('str', ['admins'], config_file['Admin'], optional=True)

        self.get_config_from_section('float', config_trade_keywords_float, config_trade)
        self.get_config_from_section('bool', config_trade_keywords_bool, config_trade)

        self.get_config_from_section('float', config_auto_push_trade_keywords_float, config_trade, optional=True)

        self.get_config_from_section('bool', ['alert_price_server_jiang_on', 'alert_price_tg_on'], config_alert)
        self.get_config_from_section('float', ['alert_price_min', 'alert_price_max', 'alert_price_tg_chat',
                                               'alert_price_interval_minute', 'alert_vol_count_minute', 'alert_vol_min',
                                               'alert_usdt_balance_over_amount']
                                     , config_alert)
        self.get_config_from_section('float', ['report_tg_chat'], config_report)
        self.get_config_from_section('int', ['price_decimal_num', 'vol_decimal_num'], config_trade)

        if self._admins:
            self._admins = [int(item) for item in self._admins.split(',')]
        else:
            self._admins = []
        if self._other_access_keys:
            self._other_access_keys = [item for item in self._other_access_keys.split(',')]
        else:
            self._other_access_keys = []
        if self._other_secret_keys:
            self._other_secret_keys = [item for item in self._other_secret_keys.split(',')]
        else:
            self._other_secret_keys = []

    def load_self_trade_config(self):
        try:
            config_file = configparser.ConfigParser(allow_no_value=True)
            config_file.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'),
                             encoding='utf-8')
        except Exception as err:
            logger.error("Can't open the config file: ", err)
            sys.exit(1)
        if not config_file.has_section('Trade'):
            logger.error("Can't find Trade section in config.")
            sys.exit(1)
        config_trade = config_file['Trade']

        self_trade_keywords = [
            'self_trade_interval',
            'self_trade_min',
            'self_trade_max',
        ]
        self.get_config_from_section('float', self_trade_keywords, config_trade)
        self.get_config_from_section('int', ['price_decimal_num', 'vol_decimal_num'], config_trade)

    def load_cross_trade_config(self):
        try:
            config_file = configparser.ConfigParser(allow_no_value=True)
            config_file.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'),
                             encoding='utf-8')
        except Exception as err:
            logger.error("Can't open the config file: ", err)
            sys.exit(1)
        if not config_file.has_section('Trade'):
            logger.error("Can't find Trade section in config.")
            sys.exit(1)
        config_trade = config_file['Trade']

        cross_trade_keywords = [
            'cross_trade_interval',
            'cross_trade_min',
            'cross_trade_max',
            'cross_depth',
            'cross_trade_price_min',
            'cross_trade_price_max',
        ]
        self.get_config_from_section('float', cross_trade_keywords, config_trade)
        self.get_config_from_section('int', ['price_decimal_num', 'vol_decimal_num'], config_trade)

    def load_cancel_config(self):
        try:
            config_file = configparser.ConfigParser(allow_no_value=True)
            config_file.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'),
                             encoding='utf-8')
        except Exception as err:
            logger.error("Can't open the config file: ", err)
            sys.exit(1)
        if not config_file.has_section('Trade'):
            logger.error("Can't find Trade section in config.")
            sys.exit(1)
        config_trade = config_file['Trade']

        self.get_config_from_section('float', ['cancel_adjustable_time'], config_trade)

    def load_all_config(self):
        self.load_config()
        self.load_self_trade_config()
        self.load_cross_trade_config()
        self.load_cancel_config()

    def get_config_from_section(self, var_type, keywords, section, optional=False):
        for item in keywords:
            if var_type == 'int':
                value = section.getint(item, 0)
            elif var_type == 'float':
                value = section.getfloat(item, 0)
            elif var_type == 'str':
                value = section.get(item, '')
            elif var_type == 'bool':
                value = section.getboolean(item, False)
            else:
                raise TypeError
            if not optional and not value and value is not False and value != 0:
                logger.warning('{} is not provided.'.format(item))
                logger.warning('{} is not provided.'.format(value))
                raise Exception
            # logger.debug('Found {}: {}'.format(item, value))
            setattr(self, '_' + item, value)

    @property
    def ACCESS_KEY(self):
        return self._access_key

    @property
    def SECRET_KEY(self):
        return self._secret_key

    @property
    def BOT_TOKEN(self):
        return self._bot_token

    @property
    def BOT_NAME(self):
        return self._bot_name

    @property
    def SERVER_JIANG_TOKEN(self):
        return self._server_jiang_token

    @property
    def SUPER_ADMIN(self):
        return self._super_admin

    @property
    def ADMINS(self):
        return self._admins

    @ADMINS.setter
    def ADMINS(self, val):
        self._admins = val

    @property
    def SYMBOL(self):
        return self._symbol

    @property
    def HTTP_API(self):
        return self._http_api

    @property
    def WEBSOCKETS_API(self):
        return self._websockets_api

    @property
    def PERIOD_TRADE_ON(self):
        return self._period_trade_on

    @property
    def DEFAULT_PERIOD_TRADE_AMOUNT_MIN(self):
        return self._default_period_trade_amount_min

    @property
    def DEFAULT_PERIOD_TRADE_AMOUNT_MAX(self):
        return self._default_period_trade_amount_max

    @property
    def DEFAULT_PERIOD_MAX_TRADE_AMOUNT(self):
        return self._default_period_max_trade_amount

    @property
    def DEFAULT_PERIOD_TRADE_INTERVAL_TIME(self):
        return self._default_period_trade_interval_time

    @property
    def DEFAULT_PERIOD_IS_OPEN(self):
        return self._default_period_is_open

    @property
    def ALERT_PRICE_SERVER_JIANG_ON(self):
        return self._alert_price_server_jiang_on

    @ALERT_PRICE_SERVER_JIANG_ON.setter
    def ALERT_PRICE_SERVER_JIANG_ON(self, val):
        self._alert_price_server_jiang_on = val

    @property
    def ALERT_PRICE_TG_ON(self):
        return self._alert_price_tg_on

    @ALERT_PRICE_TG_ON.setter
    def ALERT_PRICE_TG_ON(self, val):
        self._alert_price_tg_on = val

    @property
    def ALERT_PRICE_MIN(self):
        return self._alert_price_min

    @ALERT_PRICE_MIN.setter
    def ALERT_PRICE_MIN(self, val):
        self._alert_price_min = val

    @property
    def ALERT_PRICE_MAX(self):
        return self._alert_price_max

    @ALERT_PRICE_MAX.setter
    def ALERT_PRICE_MAX(self, val):
        self._alert_price_max = val

    @property
    def ALERT_PRICE_TG_CHAT(self):
        return self._alert_price_tg_chat

    @ALERT_PRICE_TG_CHAT.setter
    def ALERT_PRICE_TG_CHAT(self, val):
        self._alert_price_tg_chat = val

    @property
    def ALERT_PRICE_INTERVAL_MINUTE(self):
        return self._alert_price_interval_minute

    @ALERT_PRICE_INTERVAL_MINUTE.setter
    def ALERT_PRICE_INTERVAL_MINUTE(self, val):
        self._alert_price_interval_minute = val

    @property
    def alert_vol_count_minute(self):
        return self._alert_vol_count_minute

    @alert_vol_count_minute.setter
    def alert_vol_count_minute(self, val):
        self._alert_vol_count_minute = val

    @property
    def alert_vol_min(self):
        return self._alert_vol_min

    @alert_vol_min.setter
    def alert_vol_min(self, val):
        self._alert_vol_min = val

    @property
    def alert_usdt_balance_over_amount(self):
        return self._alert_usdt_balance_over_amount

    @alert_usdt_balance_over_amount.setter
    def alert_usdt_balance_over_amount(self, val):
        self._alert_usdt_balance_over_amount = val

    @property
    def REPORT_TG_CHAT(self):
        return self._report_tg_chat

    @REPORT_TG_CHAT.setter
    def REPORT_TG_CHAT(self, val):
        self._report_tg_chat = val

    @property
    def SYMBOL_NAME(self):
        return self._symbol_name

    @SYMBOL_NAME.setter
    def SYMBOL_NAME(self, val):
        self._symbol_name = val

    @property
    def OTHER_ACCESS_KEYS(self):
        return self._other_access_keys

    @OTHER_ACCESS_KEYS.setter
    def OTHER_ACCESS_KEYS(self, val):
        self._other_access_keys = val

    @property
    def OTHER_SECRET_KEYS(self):
        return self._other_secret_keys

    @OTHER_SECRET_KEYS.setter
    def OTHER_SECRET_KEYS(self, val):
        self._other_secret_keys = val

    @property
    def batch_push_trade_on(self):
        return self._batch_push_trade_on

    @batch_push_trade_on.setter
    def batch_push_trade_on(self, val):
        self._batch_push_trade_on = val

    @property
    def auto_batch_push_trade_type(self):
        return self._auto_batch_push_trade_type

    @auto_batch_push_trade_type.setter
    def auto_batch_push_trade_type(self, val):
        self._auto_batch_push_trade_type = val

    @property
    def auto_batch_push_trade_push_count(self):
        return self._auto_batch_push_trade_push_count

    @auto_batch_push_trade_push_count.setter
    def auto_batch_push_trade_push_count(self, val):
        self._auto_batch_push_trade_push_count = val

    @property
    def auto_batch_push_trade_start_price(self):
        return self._auto_batch_push_trade_start_price

    @auto_batch_push_trade_start_price.setter
    def auto_batch_push_trade_start_price(self, val):
        self._auto_batch_push_trade_start_price = val

    @property
    def auto_batch_push_trade_price_step(self):
        return self._auto_batch_push_trade_price_step

    @auto_batch_push_trade_price_step.setter
    def auto_batch_push_trade_price_step(self, val):
        self._auto_batch_push_trade_price_step = val

    @property
    def auto_batch_push_trade_push_first_amount(self):
        return self._auto_batch_push_trade_push_first_amount

    @auto_batch_push_trade_push_first_amount.setter
    def auto_batch_push_trade_push_first_amount(self, val):
        self._auto_batch_push_trade_push_first_amount = val

    @property
    def auto_batch_push_trade_up_amount(self):
        return self._auto_batch_push_trade_up_amount

    @auto_batch_push_trade_up_amount.setter
    def auto_batch_push_trade_up_amount(self, val):
        self._auto_batch_push_trade_up_amount = val

    @property
    def auto_batch_push_trade_time_interval(self):
        return self._auto_batch_push_trade_time_interval

    @auto_batch_push_trade_time_interval.setter
    def auto_batch_push_trade_time_interval(self, val):
        self._auto_batch_push_trade_time_interval = val

    @property
    def auto_batch_push_trade_type2(self):
        return self._auto_batch_push_trade_type2

    @auto_batch_push_trade_type2.setter
    def auto_batch_push_trade_type2(self, val):
        self._auto_batch_push_trade_type2 = val

    @property
    def auto_batch_push_trade_push_count2(self):
        return self._auto_batch_push_trade_push_count2

    @auto_batch_push_trade_push_count2.setter
    def auto_batch_push_trade_push_count2(self, val):
        self._auto_batch_push_trade_push_count2 = val

    @property
    def auto_batch_push_trade_start_price2(self):
        return self._auto_batch_push_trade_start_price2

    @auto_batch_push_trade_start_price2.setter
    def auto_batch_push_trade_start_price2(self, val):
        self._auto_batch_push_trade_start_price2 = val

    @property
    def auto_batch_push_trade_price_step2(self):
        return self._auto_batch_push_trade_price_step2

    @auto_batch_push_trade_price_step2.setter
    def auto_batch_push_trade_price_step2(self, val):
        self._auto_batch_push_trade_price_step2 = val

    @property
    def auto_batch_push_trade_push_first_amount2(self):
        return self._auto_batch_push_trade_push_first_amount2

    @auto_batch_push_trade_push_first_amount2.setter
    def auto_batch_push_trade_push_first_amount2(self, val):
        self._auto_batch_push_trade_push_first_amount2 = val

    @property
    def auto_batch_push_trade_up_amount2(self):
        return self._auto_batch_push_trade_up_amount2

    @auto_batch_push_trade_up_amount2.setter
    def auto_batch_push_trade_up_amount2(self, val):
        self._auto_batch_push_trade_up_amount2 = val

    @property
    def auto_batch_push_trade_time_interval2(self):
        return self._auto_batch_push_trade_time_interval2

    @auto_batch_push_trade_time_interval2.setter
    def auto_batch_push_trade_time_interval2(self, val):
        self._auto_batch_push_trade_time_interval2 = val

    @property
    def fork_trade_on(self):
        return self._fork_trade_on

    @fork_trade_on.setter
    def fork_trade_on(self, val):
        self._fork_trade_on = val

    @property
    def fork_trade_amount_max(self):
        return self._fork_trade_amount_max

    @fork_trade_amount_max.setter
    def fork_trade_amount_max(self, val):
        self._fork_trade_amount_max = val

    @property
    def fork_trade_random_amount_min(self):
        return self._fork_trade_random_amount_min

    @fork_trade_random_amount_min.setter
    def fork_trade_random_amount_min(self, val):
        self._fork_trade_random_amount_min = val

    @property
    def fork_trade_random_amount_max(self):
        return self._fork_trade_random_amount_max

    @fork_trade_random_amount_max.setter
    def fork_trade_random_amount_max(self, val):
        self._fork_trade_random_amount_max = val

    @property
    def fork_trade_interval(self):
        return self._fork_trade_interval

    @fork_trade_interval.setter
    def fork_trade_interval(self, val):
        self._fork_trade_interval = val

    # Self Trade
    @property
    def self_trade_interval(self):
        return self._self_trade_interval

    @self_trade_interval.setter
    def self_trade_interval(self, val):
        self._self_trade_interval = val

    @property
    def self_tradeMin(self):
        return self._self_trade_min

    @self_tradeMin.setter
    def self_tradeMin(self, val):
        self._self_trade_min = val

    @property
    def self_tradeMax(self):
        return self._self_trade_max

    @self_tradeMax.setter
    def self_tradeMax(self, val):
        self._self_trade_max = val

    # Cross Trade
    @property
    def cross_trade_interval(self):
        return self._cross_trade_interval

    @cross_trade_interval.setter
    def cross_trade_interval(self, val):
        self._cross_trade_interval = val

    @property
    def cross_depth(self):
        return self._cross_depth

    @cross_depth.setter
    def cross_depth(self, val):
        self._cross_depth = val

    @property
    def cross_tradeMin(self):
        return self._cross_trade_min

    @cross_tradeMin.setter
    def cross_tradeMin(self, val):
        self._cross_trade_min = val

    @property
    def cross_tradeMax(self):
        return self._cross_trade_max

    @cross_tradeMax.setter
    def cross_tradeMax(self, val):
        self._cross_trade_max = val

    @property
    def cross_trade_price_min(self):
        return self._cross_trade_price_min

    @cross_trade_price_min.setter
    def cross_trade_price_min(self, val):
        self._cross_trade_price_min = val

    @property
    def cross_trade_price_max(self):
        return self._cross_trade_price_max

    @cross_trade_price_max.setter
    def cross_trade_price_max(self, val):
        self._cross_trade_price_max = val

    # Cancel
    @property
    def cancel_adjustable_time(self):
        return self._cancel_adjustable_time

    @cancel_adjustable_time.setter
    def cancel_adjustable_time(self, val):
        self._cancel_adjustable_time = val

    # Decimal
    @property
    def price_decimal_num(self):
        return self._price_decimal_num

    @price_decimal_num.setter
    def price_decimal_num(self, val):
        self._price_decimal_num = val

    @property
    def vol_decimal_num(self):
        return self._vol_decimal_num

    @vol_decimal_num.setter
    def vol_decimal_num(self, val):
        self._vol_decimal_num = val


config = _Config()
