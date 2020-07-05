import json
import sys
from datetime import datetime
from socket import SOCK_STREAM, socket

from common.variables import (DEFAULT_IP_ADDRESS, DEFAULT_PORT, ENCODING,
                              MAX_PACKAGE_LENGTH)
from log.client_log_config import LOG


def log(func):
    def wrap_log(*args, **kwargs):
        LOG.debug(f'Вызов функции: {func.__name__} с аргументами :{args}')
        return func(*args, **kwargs)

    return wrap_log


@log
def make_sent_socket():
    addr, port = DEFAULT_IP_ADDRESS, DEFAULT_PORT
    if len(sys.argv) > 1:
        addr = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    sock = socket(type=SOCK_STREAM)
    sock.connect((addr, port))

    return sock


@log
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


@log
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


@log
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
    try:
        LOG.debug('Старт клиента')
        sock = make_sent_socket()

        message = make_presence_message('C0deMaver1ck', 'Yep, I am here!')
        answer = send_message_take_answer(sock, message)
        parse_answer(answer)

        sock.close()
    except KeyboardInterrupt:
        LOG.debug('Canceled by keyboard')
        exit(1)
    except ConnectionRefusedError:
        err_msg = 'Подключение не установлено, т.к. конечный компьютер ' + \
                'отверг запрос на подключение'
        LOG.error(err_msg)
        exit(1)
    except ConnectionResetError:
        err_msg = 'Удаленный хост принудительно разорвал ' + \
                  'существующее подключение'
        LOG.error(err_msg)
        sock.close()
        exit(1)
    except Exception as e:
        LOG.error(f'Unknown error "{e}"')


if __name__ == '__main__':
    main()
