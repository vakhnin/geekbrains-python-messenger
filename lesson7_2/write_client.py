from socket import AF_INET, SOCK_STREAM, socket

from lesson7_2.common_client import (make_msg_message, parse_args,
                                     send_message_take_answer)


def main():
    addr, port = parse_args()
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((addr, port))
        while True:
            msg = input('Ваше сообщение: ')
            if msg == 'exit':
                break
            msg = make_msg_message('Guest', msg)
            send_message_take_answer(sock, msg)


if __name__ == '__main__':
    main()
