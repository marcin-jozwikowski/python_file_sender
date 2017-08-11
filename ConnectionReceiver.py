import socket
from threading import Thread
from ConnectionBase import ConnectionBase


class ConnectionReceiver(ConnectionBase):
    file = None

    def __init__(self):
        super().__init__()
        self.set_socket()
        self.set_status_callback(lambda x: print(x))

    def start_listening(self, host=None, port=None):
        if host:
            self.host = str(host)
        if port:
            self.port = int(port)

        self.thread = Thread(target=self.listen_on_socket_thread)
        self.socket.bind((self.host, self.port))
        self.thread.start()

    def stop_listening(self):
        self.socket.close()
        self.socket = socket.socket()
        self._change_status("Idle")

    def listen_on_socket_thread(self):
        self.socket.listen(5)
        self._change_status("Listening on " + str(self.host) + ":" + str(self.port))
        while True:
            try:
                self.connection, address = self.socket.accept()
                self.file_chunks_parsed = 0
            except:
                break
            self._change_status("Got connection from " + str(address))
            line_of_file = self.connection.recv(self.chunk_size)
            while line_of_file:
                line_has_been_parsed = self.parse_received_line(line_of_file)
                if not line_has_been_parsed:
                    self.file.write(line_of_file)
                    self.file_chunks_parsed += 1
                    super()._update_status_transfer_change('Receiving ')
                if self.connection:
                    line_of_file = self.connection.recv(self.chunk_size)
                else:
                    break

            self.end_receiving()

    def parse_received_line(self, line: str):
        # file header
        if line.startswith(self.make_sendable_command(self.comm_file_header)):
            file_name = line[len(self.make_sendable_command(self.comm_file_header)):]
            self.file = open(file_name.strip(), 'wb')
            return True

        # file size
        if line.startswith(self.make_sendable_command(self.comm_file_chunks)):
            self.file_chunks_parsed = 0
            length = line[len(self.make_sendable_command(self.comm_file_chunks)):]
            self.file_chunks_total = int(length)
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

