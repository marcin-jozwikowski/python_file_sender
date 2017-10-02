import platform
import socket
import subprocess
import re
import time


# Base class for both connections used to transfer files
class ConnectionBase(object):
    _chunk_size = 1024    # single packet size - has to be the same on both ends
    _host = None          # name of the host / IP for connections
    _port = 12345         # port number for connections - defaults to 12345
    _status = None        # current class status

    _socket = None          # socket object
    _statusCallback = None  # callback for status change - simplifies communication between objects
    _connection = None      # connection object

    _file_chunks_total = 0   # total number of chunks to be sent / received
    _file_chunks_parsed = 0  # current number of chunks sent / received
    _thread = None           # thread object

    # special commands used in communication
    comm_end_trans = b'END'       # end of file - sent after last chunk
    comm_file_header = b'FILE'    # file name
    comm_file_chunks = b'CHUNKS'  # number of chunks to be sent

    # helper for formatting commands
    @staticmethod
    def make_sendable_command(text):
        return b'[' + text + b']'

    # IP extraction for Windows - 'ipconfig' command prints out all network adapters
    @staticmethod
    def _get_windows_ips():
        ips = {}
        proc = subprocess.Popen(['ipconfig'], stdout=subprocess.PIPE)
        name_regex = re.compile('^([A-Za-z0-9 \-_])+:')
        ip_regex = re.compile('^[\s]+IPv4[\w\s.]+:[\s]*(([\d]{0,3}.){4})')
        section_name = ""
        while True:
            try:
                line = proc.stdout.readline().decode("utf-8")
            except:
                # I've encountered UTF error here - it's safest to assume that it's on Adapter name
                if len(section_name) == 0:
                    line = "Unknown:"
            if line != '':
                name_search = name_regex.search(line)
                if name_search:
                    section_name = name_search.group()
                ip_search = ip_regex.search(line)
                if ip_search:
                    ip_value = ip_search.group(1).strip()
                    ips[ip_value] = ip_value + " - " + section_name[:-1]
            else:
                break
        return ips

    # constructor
    def __init__(self):
        self._host = socket.gethostname()

    # socket object setter
    def set_socket(self):
        self._socket = socket.socket()

    # status callback setter
    def set_status_callback(self, callback):
        self._statusCallback = callback

    # get all IPs available for connecting
    # it's up to the user to determine which one to use
    def get_all_ips(self):
        sys_name = platform.system()
        if sys_name == 'Windows':
            return self._get_windows_ips()
        raise Exception('System not supported: ' + sys_name)

    # port number getter
    def get_port(self):
        return self._port

    # change current status and call callback if defined
    def _change_status(self, status: str):
        self._status = status
        if hasattr(self._statusCallback, '__call__'):
            self._statusCallback(status)

    # formats command to a proper format - length must be equal to chunk_size to prevent misreading of following chunks
    def _send_standard_command(self, command, value):
        text_value = self.make_sendable_command(command) + str.encode(value)
        self._socket.send(text_value.ljust(self._chunk_size, b' '))

    # status update upon file sending
    def _update_status_transfer_change(self, message):
        if self._file_chunks_parsed % self._chunk_size == 0:
            percentage = (self._file_chunks_parsed / self._file_chunks_total) * 100
            self._change_status(str(message) + str("%.2f" % percentage) + '%')
            time.sleep(0.001)


if __name__ == '__main__':
    print("Class not callable")
