import json
import sys
from datetime import datetime
from socket import SOCK_STREAM, socket

from common.variables import (DEFAULT_IP_ADDRESS, DEFAULT_PORT, ENCODING,
                              MAX_PACKAGE_LENGTH)


def make_sent_socket():
    addr, port = DEFAULT_IP_ADDRESS, DEFAULT_PORT
    if len(sys.argv) > 1:
        addr = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    sock = socket(type=SOCK_STREAM)
    sock.connect((addr, port))

    return sock


def parse_answer(jim_obj):
    if 'response' in jim_obj.keys():
        print(f'Server response: {jim_obj["response"]}')
    else:
        print('Answer has not "response" code')
    if 'error' in jim_obj.keys():
        print(f'Server error message: {jim_obj["error"]}')
    if 'alert' in jim_obj.keys():
        print(f'Server alert message: {jim_obj["alert"]}')


def make_presence_message(account_name, status):
    return {
        'action': 'presence',
        'time': datetime.now().timestamp(),
        'type': 'status',
        'user': {
            'account_name': account_name,
            'status': status,
        }
    }


def send_message_take_answer(sock, msg):
    msg = json.dumps(msg, separators=(',', ':'))
    try:
        sock.send(msg.encode(ENCODING))
        data = sock.recv(MAX_PACKAGE_LENGTH)
        return json.loads(data.decode(ENCODING))
    except json.JSONDecodeError:
        print('Answer JSON broken')


def main():
    try:
        sock = make_sent_socket()

        message = make_presence_message('C0deMaver1ck', 'Yep, I am here!')
        answer = send_message_take_answer(sock, message)
        parse_answer(answer)

        sock.close()
    except ConnectionRefusedError:
        err_msg = 'Подключение не установлено, т.к. конечный компьютер ' + \
                'отверг запрос на подключение'
        print(err_msg)


if __name__ == '__main__':
    main()
