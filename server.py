import argparse
import json
import sys
from socket import SOCK_STREAM, socket

from common.variables import (BROKEN_JIM, DEFAULT_PORT, ENCODING,
                              MAX_CONNECTIONS, MAX_PACKAGE_LENGTH, NO_ACTION,
                              NO_TIME, NOT_BYTES, NOT_DICT, UNKNOWN_ACTION)


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
        return NOT_BYTES
    try:
        jim_obj = json.loads(data.decode(ENCODING))
        if not isinstance(jim_obj, dict):
            return NOT_DICT
        elif 'action' not in jim_obj.keys():
            return NO_ACTION
        elif 'time' not in jim_obj.keys():
            return NO_TIME
        return jim_obj
    except json.JSONDecodeError:
        return BROKEN_JIM


def choice_jim_action(jim_obj):
    if jim_obj == NOT_BYTES:
        return make_answer(500, {})
    elif jim_obj in (NO_ACTION, NO_TIME, BROKEN_JIM):
        return make_answer(400, {'error': jim_obj})
    else:
        if jim_obj['action'] == 'presence':
            return parse_presence(jim_obj)
        else:
            return make_answer(400, {'error': UNKNOWN_ACTION})


def make_answer(code, message={}):
    answer = {'response': code}
    if 'error' in message.keys():
        answer['error'] = message['error']
    elif 'alert' in message.keys():
        answer['alert'] = message['alert']
    return answer


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
        try:
            conn, addr = sock.accept()
            print(f'Соединение установлено: {addr}')
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
                except Exception as e:
                    print(f'Unknown error "{e}"')
        except KeyboardInterrupt:
            print('Canceled by keyboard')
            exit(1)
        except Exception as e:
            print(f'Unknown error "{e}"')
            exit(1)
        conn.close()


if __name__ == '__main__':
    main()
