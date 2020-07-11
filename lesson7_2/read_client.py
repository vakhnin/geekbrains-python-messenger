from socket import AF_INET, SOCK_STREAM, socket

from lesson7_2.common_client import parse_args


def main():
    addr, port = parse_args()
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((addr, port))
        while True:
            data = sock.recv(1024).decode('utf-8')
            print(data)


if __name__ == '__main__':
    main()
