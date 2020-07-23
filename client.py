import argparse
import json
import re
import sys
import threading
import time
from socket import AF_INET, SOCK_STREAM, socket

from common.variables import DEFAULT_PORT, ENCODING, MAX_PACKAGE_LENGTH
from log.client_log_config import LOG


def log(func):
    def wrap_log(*args, **kwargs):
        res = func(*args, **kwargs)
        LOG.debug(f'Log: {func.__name__}({args},{kwargs}) = {res}')
        return res

    return wrap_log


@log
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='localhost')
    parser.add_argument('-n', default='Guest')
    parser.add_argument('-p', type=int, default=DEFAULT_PORT)
    namespace = parser.parse_args(sys.argv[1:])

    return namespace.a, namespace.p, namespace.n


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
def make_presence_message(client_name, status):
    return {
        'action': 'presence',
        'time':  time.time(),
        'type': 'status',
        'user': {
            'client_name': client_name,
            'status': status,
        }
    }


@log
def make_msg_message(client_name, msg, to='#'):
    return {
        'action': 'msg',
        'time': time.time(),
        'to': to,
        'from': client_name,
        'encoding': 'utf-8',
        'message': msg,
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


@log
def cmd_help():
    print('Поддерживаемые команды:')
    print('m [сообщение] - отправить сообщение в общий чат.')
    print('p [получатель] [сообщение] - отправить приватное сообщение.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def user_input(sock, client_name):
    try:
        cmd_help()
        while True:
            msg = input('Введите команду: \n')
            msg = msg.strip()
            msg = re.split('\\s+', msg)
            if msg[0] == 'exit':
                break
            elif msg[0] == 'help':
                cmd_help()
                continue
            elif msg[0] == 'm':
                if len(msg) < 2:
                    print('Неверное количество аргументов команды.'
                          'Введите "help" для вывода списка команд')
                    continue
                msg = make_msg_message(client_name, ' '.join(msg[1:]))
            elif msg[0] == 'p':
                if len(msg) < 3:
                    print('Неверное количество аргументов команды.'
                          'Введите "help" для вывода списка команд')
                    continue
                msg = make_msg_message(client_name, ' '.join(msg[2:]), msg[1])
            else:
                print('Команда не распознана. '
                      'Введите "help" для вывода списка команд')
                continue

            msg = json.dumps(msg, separators=(',', ':'))
            sock.send(msg.encode(ENCODING))
    except Exception as e:
        LOG.debug(f'Ошибка выходного потока {e}')


@log
def user_output(sock, client_name):
    try:
        while True:
            data = sock.recv(MAX_PACKAGE_LENGTH)
            if not data:
                break
            try:
                jim_obj = json.loads(data.decode(ENCODING))
            except json.JSONDecodeError:
                LOG.error(f'Brocken jim {data}')
                continue
            if not isinstance(jim_obj, dict):
                LOG.error(f'Data not dict {jim_obj}')
                continue
            if 'response' in jim_obj.keys():
                LOG.debug(f'Получен ответ сервера {jim_obj["response"]}')
                continue
            if 'action' in jim_obj.keys():
                if jim_obj['action'] == 'msg':
                    if 'from' in jim_obj.keys() \
                            and 'message' in jim_obj.keys():
                        if 'to' in jim_obj.keys() \
                                and jim_obj['to'] == '#':
                            print(
                                f'{jim_obj["from"]}> {jim_obj["message"]}'
                            )
                        else:
                            print(
                                f'{jim_obj["from"]} (private)> '
                                f'{jim_obj["message"]}'
                            )
    except Exception as e:
        LOG.debug(f'Ошибка входного потока{e}')


def main():
    address, port, client_name = parse_args()

    try:
        print('Консольный месседжер. Клиентский модуль.')
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((address, port))
        message = make_presence_message(client_name, 'I am here!')
        answer = send_message_take_answer(sock, message)
        message = json.dumps(message, separators=(',', ':'))
        sock.send(message.encode(ENCODING))
        print('Установлено соединение с сервером.')
        LOG.info(
            f'Запущен клиент с парамертами: адрес сервера: {address}, '
            f'порт: {port}, имя пользователя: {client_name}')
        LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'\nПривет {client_name}!\n')
    except Exception as e:
        print('Соединение с сервером не установлено.')
        LOG.error(f'Соединение с сервером не установлено. Ошибка {e}')
    else:
        sender = threading.Thread(
            target=user_input, args=(sock, client_name))
        sender.daemon = True
        sender.start()

        receiver = threading.Thread(
            target=user_output, args=(sock, client_name))
        receiver.daemon = True
        receiver.start()
        LOG.debug('Запущены процессы')

        while True:
            time.sleep(10)
            if sender.is_alive() and receiver.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
