from threading import Thread

import time

from ConnectionBase import ConnectionBase


class ConnectionSender(ConnectionBase):
    file_chunks_sent = 0

    def __init__(self):
        super().__init__()
        self.host = "192.168.0.14"
        self.set_status_callback(lambda x: print(x))

    def send_file(self, file_path, host=None, port=None):
        if host:
            self.host = str(host)
        if port:
            self.port = int(port)
        thread = Thread(target=self.send_file_in_chunks(file_path))
        thread.start()

    def send_file_in_chunks(self, file_path):
        self.set_socket()
        self.socket.connect((self.host, self.port))
        self.file = open(file_path, 'rb')
        new_file_name = self.make_sendable_command(self.comm_file_header) + str.encode("__new_" + file_path)
        self.socket.send(new_file_name.ljust(self.chunk_size, b' '))
        self.change_status('Sending...')
        self.file_chunks_sent = 0
        line_of_file = self.file.read(self.chunk_size)
        while line_of_file:
            self.socket.send(line_of_file)
            line_of_file = self.file.read(self.chunk_size)
            self.file_chunks_sent += 1
            self.change_status('Sending... ' + str(self.file_chunks_sent))
        self.file.close()
        self.socket.send(self.make_sendable_command(self.comm_end_trans))
        self.change_status("Done Sending")
        self.socket.shutdown(1)
        self.socket.close()


if __name__ == '__main__':
    rec = ConnectionSender()
    rec.send_file("_test_tosend.png")
