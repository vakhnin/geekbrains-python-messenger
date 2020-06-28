import logging
import os

LOG = logging.getLogger('messenger.server')

FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s ')

logs_path = os.path.join(os.getcwd(), 'log', 'logs', 'server.log')
FILE_HANDLER = logging.FileHandler(logs_path, encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)

LOG.addHandler(FILE_HANDLER)
LOG.setLevel(logging.DEBUG)
