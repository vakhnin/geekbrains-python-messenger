import logging
import os

LOG = logging.getLogger('messenger.server')

FORMATTER = \
    logging.Formatter('%(asctime)s - %(levelname)s -  %(name)s - %(message)s ')

logs_path = os.path.join(os.getcwd(), 'log', 'logs')
if not os.path.exists(logs_path):
    os.makedirs(logs_path)
logs_path = os.path.join(logs_path, 'server.log')
FILE_HANDLER = logging.FileHandler(logs_path, encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)

LOG.addHandler(FILE_HANDLER)
LOG.setLevel(logging.DEBUG)
