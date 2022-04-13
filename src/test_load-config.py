import configparser
import os
import sys
import logging
import time


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.getLogger(__name__).setLevel(logging.INFO)
    while True:
        logger.info('Found token')
        try:
            config_file = configparser.ConfigParser(allow_no_value=True)
            config_file.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding='utf-8')
        except IOError as err:
            logger.warning("Can't open the config file: ", err)
            input('Press enter to exit.')
            sys.exit(1)
        # logger.info(config_file['General']['test_config'])
        print(config_file['API']['WebsocketsAPI'])
        config_file['API']['WebsocketsAPI'] = 'wss://wss.hotcoinfin.com/trade/multiple'
        with open(os.path.join(os.path.dirname(__file__), 'config.ini'), 'w') as configfile:
            config_file.write(configfile)
        time.sleep(3)
