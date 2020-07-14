import argparse
import json
import sys
import time
from socket import AF_INET, SOCK_STREAM, socket

from common.decorators import log
from common.variables import DEFAULT_PORT, ENCODING, MAX_PACKAGE_LENGTH
from log.client_log_config import LOG


@log(LOG)
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='localhost')
    parser.add_argument('-n', default='Guest')
    parser.add_argument('-p', type=int, default=DEFAULT_PORT)
    namespace = parser.parse_args(sys.argv[1:])

    return namespace.a, namespace.p, namespace.n


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


def main():
    address, port, account_name = parse_args()
    print(f'Привет, {account_name}!')
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((address, port))
        while True:
            msg = input('Ваше сообщение: ')
            if msg == 'exit':
                break
            msg = make_msg_message(account_name, msg)
            send_message_take_answer(sock, msg)


if __name__ == '__main__':
    main()
