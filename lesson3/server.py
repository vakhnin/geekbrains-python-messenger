# Реализовать простое клиент-серверное взаимодействие по
# протоколу JIM (JSON instant messaging):
#
# клиент отправляет запрос серверу;
#
# сервер отвечает соответствующим кодом результата. Клиент и сервер должны быть
# реализованы в виде отдельных скриптов, содержащих соответствующие функции.
#
# Функции клиента:
# сформировать presence-сообщение;
# отправить сообщение серверу;
# получить ответ сервера;
# разобрать сообщение сервера;
# параметры командной строки скрипта client.py <addr> [<port>]:
# addr — ip-адрес сервера; port — tcp-порт на сервере, по умолчанию 7777.
#
# Функции сервера:
# принимает сообщение клиента;
# формирует ответ клиенту;
# отправляет ответ клиенту;
# имеет параметры командной строки:
# -p <port> — TCP-порт для работы (по умолчанию использует 7777);
# -a <addr> — IP-адрес для прослушивания
# (по умолчанию слушает все доступные адреса).
import json
from socket import SOCK_STREAM, socket

sock = socket(type=SOCK_STREAM)
sock.bind(('', 9090))
sock.listen(5)

while True:
    conn, addr = sock.accept()

    print(f'Соединение установлено: {addr}')

    try:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                jim_obj = json.loads(data.decode('utf-8'))
                print(jim_obj)
                conn.send(data.upper())
            except json.JSONDecodeError:
                jim_answer = {
                    'response': 400,
                    'error': 'JSON broken'
                }
                answer = json.dumps(jim_answer, separators=(',', ':'))
                conn.send(answer.encode('utf-8'))
            except ConnectionResetError:
                err_msg = 'Удаленный хост принудительно разорвал ' + \
                    'существующее подключение'
                print(err_msg)
                conn.close()
    finally:
        conn.close()
