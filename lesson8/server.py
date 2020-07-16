import argparse
import json
import select
import sys
from collections import deque
from socket import SOCK_STREAM, socket

from common.decorators import log
from common.variables import (BROKEN_JIM, DEFAULT_PORT, ENCODING,
                              MAX_CONNECTIONS, MAX_PACKAGE_LENGTH, NO_ACTION,
                              NO_TIME, NOT_BYTES, NOT_DICT, UNKNOWN_ACTION)
from log.server_log_config import LOG


@log(LOG)
def make_listen_socket():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='')
    parser.add_argument('-p', type=int, default=DEFAULT_PORT)
    namespace = parser.parse_args(sys.argv[1:])

    sock = socket(type=SOCK_STREAM)
    sock.bind((namespace.a, namespace.p))
    sock.listen(MAX_CONNECTIONS)
    sock.settimeout(0.2)
    return sock


@log(LOG)
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
        LOG.error(BROKEN_JIM)
        return BROKEN_JIM


@log(LOG)
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


@log(LOG)
def make_answer(code, message={}):
    answer = {'response': code}
    if 'error' in message.keys():
        answer['error'] = message['error']
    elif 'alert' in message.keys():
        answer['alert'] = message['alert']
    return answer


@log(LOG)
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


@log(LOG)
def read_requests(r_clients, clients_data):
    for sock in r_clients:
        if sock not in clients_data.keys():
            return
        try:
            msg = sock.recv(MAX_PACKAGE_LENGTH).decode('utf-8')
            try:
                jim_obj = json.loads(msg)
            except json.JSONDecodeError:
                LOG.error(f'Brocken jim {msg}')
                continue

            answer = make_answer(200)
            answer = json.dumps(answer, separators=(',', ':'))
            clients_data[sock]['answ_for_send'].append(answer)

            if not isinstance(jim_obj, dict):
                LOG.error(f'Data not dict {jim_obj}')
                continue
            if 'action' in jim_obj.keys():
                if jim_obj['action'] == 'presence':
                    if 'user' in jim_obj.keys() \
                            and isinstance(jim_obj['user'], dict) \
                            and 'client_name' in jim_obj['user'].keys():
                        clients_data[sock]['client_name'] = \
                            jim_obj['user']['client_name']
                        continue
                elif jim_obj['action'] == 'msg':
                    for _, value in clients_data.items():
                        if jim_obj['to'] == '#' \
                                or jim_obj['to'] == value['client_name']:
                            value['msg_for_send'].append(msg)
        except Exception:
            print(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
            sock.close()
            del clients_data[sock]


@log(LOG)
def write_responses(w_clients, clients_data):
    for sock in w_clients:
        if sock not in clients_data.keys():
            return
        try:
            if len(clients_data[sock]['answ_for_send']):
                msg = clients_data[sock]['answ_for_send'].pop()
                sock.send(msg.encode('utf-8'))
            elif len(clients_data[sock]['msg_for_send']):
                msg = clients_data[sock]['msg_for_send'].pop()
                sock.send(msg.encode('utf-8'))
        except Exception:
            print(
                f'Клиент {sock.fileno()} {sock.getpeername()} отключился'
            )
            sock.close()
            del clients_data[sock]


def main():
    LOG.debug('Старт сервера')
    print('Старт сервера')

    clients_data = {}
    sock = make_listen_socket()
    while True:
        try:
            conn, addr = sock.accept()
            print(f'Соединение установлено: {addr}')
        except OSError:
            pass
        else:
            print('Получен запрос на соединение от %s' % str(addr))
            clients_data[conn] = \
                {
                    'client_name': '',
                    'msg_for_send': deque(maxlen=100),
                    'answ_for_send': deque(maxlen=100),
                }
        finally:
            wait = 0
            r = []
            w = []
            try:
                r, w, e = \
                    select.select(
                        clients_data.keys(), clients_data.keys(), [], wait)
                LOG.debug(f'Ошибки сокетов {e}')
            except Exception:
                pass

            read_requests(r, clients_data)
            write_responses(w, clients_data)


if __name__ == '__main__':
    main()
