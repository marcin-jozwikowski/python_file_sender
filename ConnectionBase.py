import platform
import socket

import subprocess

import re


class ConnectionBase(object):
    chunk_size = 1024
    socket = None
    host = None
    port = 12345
    status = None
    statusCallback = None
    connection = None
    file = None
    file_chunks_total = 0


    comm_end_trans = b'END'
    comm_file_header = b'FILE'
    comm_file_chunks = b'CHUNKS'

    def __init__(self):
        self.socket = socket.socket()
        self.host = socket.gethostname()

    @staticmethod
    def make_sendable_command(text):
        return b'[' + text + b']'

    def change_status(self, status: str):
        self.status = status
        if hasattr(self.statusCallback, '__call__'):
            self.statusCallback(status)

    def set_status_callback(self, callback):
        self.statusCallback = callback


if __name__ == '__main__':
    print("Class not callable")