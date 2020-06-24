import json
import sys
from datetime import datetime
from socket import SOCK_STREAM, socket

from lesson3.common.variables import (DEFAULT_IP_ADDRESS, DEFAULT_PORT,
                                      ENCODING, MAX_PACKAGE_LENGTH)


def parse_answer(jim_obj):
    if 'response' in jim_obj.keys():
        print(f'Server response: {jim_obj["response"]}')
    else:
        print('Answer has not "response" code')
    if 'error' in jim_obj.keys():
        print(f'Server error message: {jim_obj["error"]}')
    if 'alert' in jim_obj.keys():
        print(f'Server alert message: {jim_obj["alert"]}')


def presence_send(sock_, account_name, status):
    jim_msg = {
        'action': 'presence',
        'time': datetime.now().timestamp(),
        'type': 'status',
        'user': {
            'account_name': account_name,
            'status': status,
        }
    }
    msg = json.dumps(jim_msg, separators=(',', ':'))
    sock_.send(msg.encode(ENCODING))
    try:
        data = sock.recv(MAX_PACKAGE_LENGTH)
        jim_obj = json.loads(data.decode(ENCODING))
        parse_answer(jim_obj)
    except json.JSONDecodeError:
        print('Answer JSON broken')


try:
    addr, port = DEFAULT_IP_ADDRESS, DEFAULT_PORT
    if len(sys.argv) > 1:
        addr = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    sock = socket(type=SOCK_STREAM)
    sock.connect((addr, port))

    presence_send(sock, 'C0deMaver1ck', 'Yep, I am here!')
except ConnectionRefusedError:
    err_msg = 'Подключение не установлено, т.к. конечный компьютер ' + \
            'отверг запрос на подключение'
    print(err_msg)
finally:
    sock.close()
