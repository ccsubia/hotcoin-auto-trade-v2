import configparser
import os
import logging
import sys

logger = logging.getLogger(__name__)


class _Config:
    def __init__(self):
        self._access_key = ''
        self._secret_key = ''
        self._bot_token = ''
        self._bot_name = ''
        self._server_jiang_token = ''
        self._super_admin = ''
        self._symbol = ''
        self._http_api = ''
        self._websockets_api = ''
        self._admins = ''
        self._depth_param = ''
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

    def load_config(self):
        logger.debug('Found token')
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

        config_secret_keywords_str = [
            'access_key',
            'secret_key',
            'bot_token',
            'bot_name',
        ]
        config_secret_keywords_optional_str = [
            'server_jiang_token',
        ]
        config_api_keywords_str = [
            'symbol',
            'http_api',
            'websockets_api',
        ]
        config_period_trade_keywords_float = [
            'default_period_trade_amount_min',
            'default_period_trade_amount_max',
            'default_period_max_trade_amount',
            'default_period_trade_interval_time',
        ]

        self.get_config_from_section('str', config_secret_keywords_str, config_secret)
        self.get_config_from_section('str', config_secret_keywords_optional_str, config_secret, optional=True)
        self.get_config_from_section('str', config_api_keywords_str, config_api)

        self.get_config_from_section('str', ['super_admin'], config_file['Admin'])
        self.get_config_from_section('str', ['admins'], config_file['Admin'], optional=True)

        self.get_config_from_section('float', config_period_trade_keywords_float, config_trade)
        self.get_config_from_section('bool', ['period_trade_on', 'default_period_is_open'], config_trade)

        self.get_config_from_section('bool', ['alert_price_server_jiang_on', 'alert_price_tg_on'], config_alert)
        self.get_config_from_section('float', ['alert_price_min', 'alert_price_max', 'alert_price_tg_chat',
                                               'alert_price_interval_minute'], config_alert)

        if self._admins:
            self._admins = [int(item) for item in self._admins.split(',')]
        else:
            self._admins = []
        self._depth_param = '{"sub": "market.' + self._symbol + '.trade.depth"}'

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
            if not optional and not value and value is not False:
                logger.warning('{} is not provided.'.format(item))
                raise Exception
            logger.debug('Found {}: {}'.format(item, value))
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
    def DEPTH_PARAM(self):
        return self._depth_param

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


config = _Config()
