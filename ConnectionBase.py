import platform
import socket
import subprocess
import re
import time


class ConnectionBase(object):
    chunk_size = 1024
    host = None
    port = 12345
    status = None

    socket = None
    statusCallback = None
    connection = None

    file_chunks_total = 0
    file_chunks_parsed = 0
    thread = None

    comm_end_trans = b'END'
    comm_file_header = b'FILE'
    comm_file_chunks = b'CHUNKS'

    def __init__(self):
        self.host = socket.gethostname()

    def set_socket(self):
        self.socket = socket.socket()

    @staticmethod
    def make_sendable_command(text):
        return b'[' + text + b']'

    def _change_status(self, status: str):
        self.status = status
        if hasattr(self.statusCallback, '__call__'):
            self.statusCallback(status)

    def set_status_callback(self, callback):
        self.statusCallback = callback

    def get_all_ips(self):
        sys_name = platform.system()
        if sys_name == 'Windows':
            return self._get_windows_ips()
        raise Exception('System not supported: ' + sys_name)

    def _get_windows_ips(self):
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

    def _send_standard_command(self, command, value):
        text_value = self.make_sendable_command(command) + str.encode(value)
        self.socket.send(text_value.ljust(self.chunk_size, b' '))

    def _update_status_transfer_change(self, message):
        if self.file_chunks_parsed % self.chunk_size == 0:
            percentage = (self.file_chunks_parsed / self.file_chunks_total) * 100
            self._change_status(str(message) + str("%.2f" % percentage) + '%')
            time.sleep(0.001)

if __name__ == '__main__':
    print("Class not callable")
