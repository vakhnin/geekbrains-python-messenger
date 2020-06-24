import argparse
import json
import sys
from socket import SOCK_STREAM, socket

from common.variables import (BROKENJIM, DEFAULT_PORT, ENCODING,
                              MAX_CONNECTIONS, MAX_PACKAGE_LENGTH, NOACTION,
                              NOTBYTES, NOTIME, UNKNOWNACTION)


def make_listen_socket():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='')
    parser.add_argument('-p', type=int, default=DEFAULT_PORT)
    namespace = parser.parse_args(sys.argv[1:])

    sock = socket(type=SOCK_STREAM)
    sock.bind((namespace.a, namespace.p))
    sock.listen(MAX_CONNECTIONS)
    return sock


def parse_received_bytes(data):
    if not isinstance(data, bytes):
        return NOTBYTES
    try:
        jim_obj = json.loads(data.decode(ENCODING))
        if 'action' not in jim_obj.keys():
            return NOACTION
        elif 'time' not in jim_obj.keys():
            return NOTIME
        return jim_obj
    except json.JSONDecodeError:
        return BROKENJIM


def choice_jim_action(jim_obj):
    if jim_obj == NOTBYTES:
        return make_answer(500, {})
    elif jim_obj in (NOACTION, NOTIME, BROKENJIM):
        return make_answer(400, {'error': jim_obj})
    else:
        if jim_obj['action'] == 'presence':
            return parse_presence(jim_obj)
        else:
            return make_answer(400, {'error': UNKNOWNACTION})


def make_answer(code, message={}):
    answer_ = {'response': code}
    if 'error' in message.keys():
        answer_['error'] = message['error']
    elif 'alert' in message.keys():
        answer_['alert'] = message['alert']
    return answer_


def parse_presence(jim_obj):
    if 'user' not in jim_obj.keys():
        return make_answer(400, {'error': 'Request has no "user"'})
    elif type(jim_obj['user']) != dict:
        return make_answer(400, {'error': '"user" is not dict'})
    elif 'account_name' not in jim_obj['user'].keys():
        return make_answer(400, {'error': '"user" has no "account_name"'})
    elif not jim_obj['user']['account_name']:
        return make_answer(400, {'error': '"account_name" is empty'})
    else:
        print(f'User {jim_obj["user"]["account_name"]} is presence')
        if 'status' in jim_obj['user'].keys() \
                and jim_obj['user']['status']:
            print(f'Status user{jim_obj["user"]["account_name"]} is "' +
                  jim_obj['user']['status'] + '"')
        return make_answer(200)


def main():
    sock = make_listen_socket()
    while True:
        conn, addr = sock.accept()
        print(f'Соединение установлено: {addr}')

        try:
            while True:
                try:
                    data = conn.recv(MAX_PACKAGE_LENGTH)
                    if not data:
                        break
                    jim_obj = parse_received_bytes(data)
                    answer = choice_jim_action(jim_obj)
                    answer = json.dumps(answer, separators=(',', ':'))
                    conn.send(answer.encode(ENCODING))
                except ConnectionResetError:
                    err_msg = 'Удаленный хост принудительно разорвал ' + \
                        'существующее подключение'
                    print(err_msg)
                    conn.close()
        finally:
            conn.close()


if __name__ == '__main__':
    main()
