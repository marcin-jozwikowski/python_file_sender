from threading import Thread

import time

import os

from ConnectionBase import ConnectionBase


class ConnectionSender(ConnectionBase):
    def __init__(self):
        super().__init__()
        self._thread = None
        self._host = ""
        self.set_status_callback(lambda x: print(x))

    def send_file(self, file_path, file_name=None, host=None, port=None):
        if host:
            self._host = str(host)
        if port:
            self._port = int(port)
        self._thread = Thread(target=self._send_file_in_chunks(file_path, file_name))
        self._thread.start()

    def _send_file_in_chunks(self, file_path, file_name=None):
        self.set_socket()
        self._socket.connect((self._host, self._port))
        file = self._open_file_for_sending(file_path, file_name)
        line_of_file = file.read(self._chunk_size)
        while line_of_file:
            self._socket.send(line_of_file)
            line_of_file = file.read(self._chunk_size)
            self._file_chunks_parsed += 1
            super()._update_status_transfer_change('Sending ')
        file.close()
        self._socket.send(self.make_sendable_command(self.comm_end_trans))
        self._change_status("Done Sending")
        self._socket.shutdown(1)
        self._socket.close()

    def _open_file_for_sending(self, file_path, file_name=None):
        file = open(file_path, 'rb')
        file_name = os.path.basename(file_path) if file_name is None else file_name
        self._file_chunks_total = self.get_file_size(file_path)
        self._send_standard_command(self.comm_file_header, file_name)
        self._send_standard_command(self.comm_file_chunks, str(round(self._file_chunks_total)))
        self._file_chunks_parsed = 0
        return file

    def get_file_size(self, file_path):
        return os.stat(file_path).st_size / self._chunk_size


if __name__ == '__main__':
    print("Class not callable")

