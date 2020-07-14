import argparse
import json
import sys
import threading
import time
from socket import AF_INET, SOCK_STREAM, socket

from common.decorators import log
from common.variables import DEFAULT_PORT, ENCODING, MAX_PACKAGE_LENGTH
from lesson8.server import parse_received_bytes
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


@log(LOG)
def make_msg_message(client_name, msg, to='#'):
    return {
        'action': 'msg',
        'time': time.time(),
        'to': to,
        'from': client_name,
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


@log(LOG)
def user_input(sock, client_name):
    while True:
        msg = input('Ваше сообщение: ')
        if msg == 'exit':
            break
        msg = make_msg_message(client_name, msg)
        send_message_take_answer(sock, msg)


@log(LOG)
def user_output(sock, client_name):
    while True:
        data = sock.recv(MAX_PACKAGE_LENGTH)
        if not data:
            break
        jim_obj = parse_received_bytes(data)
        print(f'{jim_obj["from"]}> {jim_obj["message"]}')


def main():
    address, port, client_name = parse_args()

    try:
        print('Консольный месседжер. Клиентский модуль.')
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((address, port))
        message = make_presence_message(client_name, 'I am here!')
        answer = send_message_take_answer(sock, message)
        LOG.info(
            f'Запущен клиент с парамертами: адрес сервера: {address}, '
            f'порт: {port}, имя пользователя: {client_name}')
        LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Привет {client_name}!')
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
