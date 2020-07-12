from socket import AF_INET, SOCK_STREAM, socket

from common.variables import MAX_PACKAGE_LENGTH
from lesson7_2.common_client import parse_args
from lesson7_2.server import parse_received_bytes


def main():
    address, port = parse_args()
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((address, port))
        while True:
            data = sock.recv(MAX_PACKAGE_LENGTH)
            if not data:
                break
            jim_obj = parse_received_bytes(data)
            print(f'{jim_obj["from"]}> {jim_obj["message"]}')


if __name__ == '__main__':
    main()
