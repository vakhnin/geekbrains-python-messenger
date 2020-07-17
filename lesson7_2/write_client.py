from socket import AF_INET, SOCK_STREAM, socket

from lesson7_2.common_client import (make_msg_message, parse_args,
                                     send_message_take_answer)


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
