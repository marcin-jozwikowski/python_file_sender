import socket
from threading import Thread

import os

from os.path import join

from ConnectionBase import ConnectionBase


class ConnectionReceiver(ConnectionBase):
    file = None

    def __init__(self):
        super().__init__()
        self.set_socket()
        self.set_status_callback(lambda x: print(x))

    def start_listening(self, host=None, port=None):
        if host:
            self._host = str(host)
        if port:
            self._port = int(port)

        self._thread = Thread(target=self.listen_on_socket_thread)
        self._socket.bind((self._host, self._port))
        self._thread.start()

    def stop_listening(self):
        self._socket.close()
        self._socket = socket.socket()
        self._change_status("Idle")

    def listen_on_socket_thread(self):
        self._socket.listen(5)
        self._change_status("Listening on " + str(self._host) + ":" + str(self._port))
        while True:
            try:
                self._connection, address = self._socket.accept()
                self._file_chunks_parsed = 0
            except:
                break
            self._change_status("Got connection from " + str(address))
            line_of_file = self._connection.recv(self._chunk_size)
            while line_of_file:
                line_has_been_parsed = self.parse_received_line(line_of_file)
                if not line_has_been_parsed:
                    self.file.write(line_of_file)
                    self._file_chunks_parsed += 1
                    super()._update_status_transfer_change('Receiving ')
                if self._connection:
                    line_of_file = self._connection.recv(self._chunk_size)
                else:
                    break

            self.end_receiving()

    def parse_received_line(self, line: str):
        # file header
        if line.startswith(self.make_sendable_command(self.comm_file_header)):
            file_name = line[len(self.make_sendable_command(self.comm_file_header)):]
            file_path = join(os.getcwd(), file_name.strip().decode())
            file_path_directory = os.path.dirname(file_path)
            if not os.path.exists(file_path_directory):
                os.makedirs(file_path_directory)
            self.file = open(file_path, 'wb')
            return True

        # file size
        if line.startswith(self.make_sendable_command(self.comm_file_chunks)):
            self._file_chunks_parsed = 0
            length = line[len(self.make_sendable_command(self.comm_file_chunks)):]
            self._file_chunks_total = int(length)
            return True

        # end command
        if line.startswith(self.make_sendable_command(self.comm_end_trans)):
            self.end_receiving()
            return True

    def end_receiving(self):
        if not self.file.closed:
            self.file.close()
        self._change_status("Done Receiving")


if __name__ == '__main__':
    print("Class not callable")

