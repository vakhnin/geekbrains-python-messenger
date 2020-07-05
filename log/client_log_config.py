import logging
import os
from logging.handlers import RotatingFileHandler

LOG = logging.getLogger('messenger.client')

FORMATTER = \
    logging.Formatter('%(asctime)s - %(levelname)s -  %(name)s - %(message)s ')

LOGS_PATH = os.path.join(os.getcwd(), 'log', 'logs')
if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)
LOGS_PATH = os.path.join(LOGS_PATH, 'client.log')

ROTATION_FILE_HANDLER = \
    RotatingFileHandler(LOGS_PATH, maxBytes=100000,
                        backupCount=5, encoding='utf-8')
ROTATION_FILE_HANDLER.setFormatter(FORMATTER)
LOG.addHandler(ROTATION_FILE_HANDLER)

LOG.setLevel(logging.DEBUG)
