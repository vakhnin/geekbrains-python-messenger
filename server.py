import argparse
import json
import sys
from socket import SOCK_STREAM, socket

from common.variables import DEFAULT_PORT, ENCODING, MAX_PACKAGE_LENGTH


def create_parser():
    parser_ = argparse.ArgumentParser()
    parser_.add_argument('-a', default='')
    parser_.add_argument('-p', type=int, default=DEFAULT_PORT)
    return parser_


def make_answer(code, message={}):
    answer_ = {'response': code}
    if 'error' in message.keys():
        answer_['error'] = message['error']
    elif 'alert' in message.keys():
        answer_['alert'] = message['alert']
    return answer_


def parse_presence(jim_obj_):
    if 'user' not in jim_obj_.keys():
        return make_answer(400, {'error': 'Request has no "user"'})
    elif type(jim_obj_['user']) != dict:
        return make_answer(400, {'error': '"user" is not dict'})
    elif 'account_name' not in jim_obj_['user'].keys():
        return make_answer(400, {'error': '"user" has no "account_name"'})
    elif not jim_obj_['user']['account_name']:
        return make_answer(400, {'error': '"account_name" is empty'})
    else:
        print(f'User {jim_obj_["user"]["account_name"]} is presence')
        if 'status' in jim_obj_['user'].keys() \
                and jim_obj_['user']['status']:
            print(f'Status user{jim_obj_["user"]["account_name"]} is "' +
                  jim_obj_['user']['status'] + '"')
        return make_answer(200)


def main():
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    sock = socket(type=SOCK_STREAM)
    sock.bind((namespace.a, namespace.p))
    sock.listen(5)

    while True:
        conn, addr = sock.accept()

        print(f'Соединение установлено: {addr}')

        try:
            while True:
                try:
                    data = conn.recv(MAX_PACKAGE_LENGTH)
                    if not data:
                        break
                    jim_obj = json.loads(data.decode(ENCODING))
                    if 'action' not in jim_obj.keys():
                        ans_str = 'Request has no "action"'
                        answer = make_answer(400, {'error': ans_str})
                    elif 'time' not in jim_obj.keys():
                        ans_str = 'Request has no "time""'
                        answer = make_answer(400, {'error': ans_str})
                    else:
                        if jim_obj['action'] == 'presence':
                            answer = parse_presence(jim_obj)
                        else:
                            answer = make_answer(400,
                                                 {'error': 'Unknown action'})
                    answer = json.dumps(answer, separators=(',', ':'))
                    conn.send(answer.encode(ENCODING))
                except json.JSONDecodeError:
                    answer = make_answer(400, {'error': 'JSON broken'})
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
