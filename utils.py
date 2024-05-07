import logging
from logging.handlers import RotatingFileHandler
import json

with open('configs/findArb.conf', 'r') as file:
    configs = json.load(file)

with open(configs['file_pairs'], 'r') as file:
    symbols = json.load(file)

exchanges = configs['exchanges']
minimal_profit = configs['minimal_profit']
max_profit = configs['max_profit']
max_amount = configs['max_amount']

# Config system log.
log_level_config = {'debug': logging.DEBUG, 'info': logging.INFO} 
log_level = log_level_config[configs['logging']['loglevel']]
log_file = configs['logging']['logfile']

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# create a file handler
handler = RotatingFileHandler(log_file, mode='a', maxBytes=100*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
handler.setLevel(log_level)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s  %(filename)s:%(lineno)s -   %(funcName)s() -> %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
