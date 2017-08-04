from threading import Thread
from ConnectionBase import ConnectionBase


class ConnectionReceiver(ConnectionBase):
    file_chunks_received = 0

    def __init__(self):
        super().__init__()
        self.set_status_callback(lambda x: print(x))

    def start_listening(self, host=None, port=None):
        if host:
            self.host = host
        if port:
            self.port = port

        self.socket.bind((self.host, self.port))
        Thread(target=self.listen_on_socket).start()

    def listen_on_socket(self):
        self.socket.listen(5)
        while True:
            self.change_status("Listening on port " + str(self.port))
            self.connection, address = self.socket.accept()
            self.change_status("Got connection from " + str(address))
            line_of_file = self.connection.recv(self.chunk_size)
            while line_of_file:
                line_has_been_parsed = self.parse_received_line(line_of_file)
                if not line_has_been_parsed:
                    self.file.write(line_of_file)
                    self.file_chunks_received += 1
                if self.connection:
                    line_of_file = self.connection.recv(self.chunk_size)
                else:
                    break

            self.change_status("Done Receiving")

    def parse_received_line(self, line: str):
        # file header
        if line.startswith(self.make_sendable_command(self.comm_file_header)):
            file_name = line[len(self.make_sendable_command(self.comm_file_header)):]
            self.change_status("FileName  " + str(file_name))
            self.file = open(file_name, 'wb')
            return True

        # file size
        if line.startswith(self.make_sendable_command(self.comm_file_chunks)):
            self.file_chunks_received = 0
            self.file_chunks_total = int(line[len(self.make_sendable_command(self.comm_file_header)):])
            self.change_status("File chunks " + str(self.file_chunks_total))
            return True

        # end command
        if line.startswith(self.make_sendable_command(self.comm_end_trans)):
            self.end_receiving()
            self.change_status("End Signal")
            return True

    def end_receiving(self):
        self.file.close()
        self.connection = None


if __name__ == '__main__':
    rec = ConnectionReceiver()
    rec.start_listening()
