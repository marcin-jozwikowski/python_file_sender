from threading import Thread
from ConnectionBase import ConnectionBase


class ConnectionSender(ConnectionBase):
    file_chunks_sent = 0

    def __init__(self):
        super().__init__()
        self.set_status_callback(lambda x: print(x))

    def send_file(self, file_path, host=None, port=None):
        if host:
            self.host = host
        if port:
            self.port = port
        Thread(target=self.send_file_in_chunks(file_path)).start()

    def send_file_in_chunks(self, file_path):
        self.socket.connect((self.host, self.port))
        self.file = open(file_path, 'rb')
        self.socket.send(b'[FILE]new_' + file_path)
        self.change_status('Sending...')
        line_of_file = self.file.read(self.chunk_size)
        while line_of_file:
            self.change_status('Sending...')
            self.socket.send(line_of_file)
            line_of_file = self.file.read(self.chunk_size)
        self.file.close()
        self.socket.send(b'[END]')
        self.change_status("Done Sending")
        self.socket.shutdown(1)
        self.socket.close()


if __name__ == '__main__':
    rec = ConnectionSender()
    rec.send_file(b'tosend.png')
