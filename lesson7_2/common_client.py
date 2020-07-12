import json
import sys
import time
from socket import SOCK_STREAM, socket

from common.decorators import log
from common.variables import (DEFAULT_IP_ADDRESS, DEFAULT_PORT, ENCODING,
                              MAX_PACKAGE_LENGTH)
from log.client_log_config import LOG


@log(LOG)
def parse_args():
    addr, port = DEFAULT_IP_ADDRESS, DEFAULT_PORT
    if len(sys.argv) > 1:
        addr = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    sock = socket(type=SOCK_STREAM)
    sock.connect((addr, port))

    return addr, port


@log(LOG)
def parse_answer(jim_obj):
    if not isinstance(jim_obj, dict):
        print('Server answer not dict')
        return
    if 'response' in jim_obj.keys():
        print(f'Server answer: {jim_obj["response"]}')
    else:
        print('Answer has not "response" code')
    if 'error' in jim_obj.keys():
        print(f'Server error message: {jim_obj["error"]}')
    if 'alert' in jim_obj.keys():
        print(f'Server alert message: {jim_obj["alert"]}')


@log(LOG)
def make_presence_message(account_name, status):
    return {
        'action': 'presence',
        'time':  time.time(),
        'type': 'status',
        'user': {
            'account_name': account_name,
            'status': status,
        }
    }


@log(LOG)
def make_msg_message(account_name, msg, to='#'):
    return {
        'action': 'msg',
        'time': time.time(),
        'to': to,
        'from': account_name,
        'encoding': 'utf-8',
        'message': msg,
    }


@log(LOG)
def send_message_take_answer(sock, msg):
    msg = json.dumps(msg, separators=(',', ':'))
    try:
        sock.send(msg.encode(ENCODING))
        data = sock.recv(MAX_PACKAGE_LENGTH)
        return json.loads(data.decode(ENCODING))
    except json.JSONDecodeError:
        LOG.error('Answer JSON broken')
        return {}
