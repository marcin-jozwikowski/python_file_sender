from threading import Thread

import time

import os

from ConnectionBase import ConnectionBase


class ConnectionSender(ConnectionBase):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.host = ""
        self.set_status_callback(lambda x: print(x))

    def send_file(self, file_path, host=None, port=None):
        if host:
            self.host = str(host)
        if port:
            self.port = int(port)
        self.thread = Thread(target=self._send_file_in_chunks(file_path))
        self.thread.start()

    def _send_file_in_chunks(self, file_path):
        self.set_socket()
        self.socket.connect((self.host, self.port))
        file = self._open_file_for_sending(file_path)
        line_of_file = file.read(self.chunk_size)
        while line_of_file:
            self.socket.send(line_of_file)
            line_of_file = file.read(self.chunk_size)
            self.file_chunks_parsed += 1
            super()._update_status_transfer_change('Sending ')
        file.close()
        self.socket.send(self.make_sendable_command(self.comm_end_trans))
        self._change_status("Done Sending")
        self.socket.shutdown(1)
        self.socket.close()

    def _open_file_for_sending(self, file_path):
        file = open(file_path, 'rb')
        self.file_chunks_total = self.get_file_size(file_path)
        self._send_standard_command(self.comm_file_header, os.path.basename(file_path))
        self._send_standard_command(self.comm_file_chunks, str(round(self.file_chunks_total)))
        self.file_chunks_parsed = 0
        return file

    def get_file_size(self, file_path):
        return os.stat(file_path).st_size / self.chunk_size


if __name__ == '__main__':
    print("Class not callable")

