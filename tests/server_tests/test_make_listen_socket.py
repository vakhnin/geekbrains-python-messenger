import sys
import unittest

from client import make_sent_socket
from common.variables import MAX_PACKAGE_LENGTH
from server import make_listen_socket


class TestMakeListenSocketFunction(unittest.TestCase):
    def test_make_listen_socket(self):
        tmp = sys.argv
        sys.argv = ['server.py', '-a', 'localhost', '-p', '7777']
        sock1 = make_listen_socket()
        sys.argv = tmp
        sock2 = make_sent_socket()

        sock2.send(b'listen test')

        conn, addr = sock1.accept()
        data = conn.recv(MAX_PACKAGE_LENGTH)

        sock1.close()
        sock2.close()
        self.assertEqual(data, b'listen test')
