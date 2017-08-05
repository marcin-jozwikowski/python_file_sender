from tkinter import *
from tkinter.ttk import *

from ConnectionReceiver import ConnectionReceiver


class FileTransfer(object):

    connection_receiver = None
    all_ips = {}

    def __init__(self):
        self.connection_receiver = ConnectionReceiver()
        self.connection_receiver.set_status_callback(self.receiver_status_callback)
        self.all_ips = self.connection_receiver.get_all_ips()

        self.top = Tk()

        receiver_frame = Frame(self.top)
        receiver_label = Label(receiver_frame, text='Receiver', font=('Halvetica', 12, 'bold'))
        receiver_label.pack()

        receiver_ips_selector = Frame(receiver_frame)
        self.port_number_value = StringVar()
        self.port_number_value.set(ConnectionReceiver.port)
        port_number = Entry(receiver_ips_selector, textvariable=self.port_number_value)
        port_number.pack(side=RIGHT)
        self.receiver_ip_box_value = StringVar()
        receiver_ip_box = Combobox(receiver_ips_selector, textvariable=self.receiver_ip_box_value)
        receiver_ip_box['values'] = list(self.all_ips.values())
        receiver_ip_box.current(0)
        receiver_ip_box.pack(side=LEFT, fill=BOTH, expand=1)
        receiver_ips_selector.pack(fill=BOTH, expand=1)

        self.receiver_status = StringVar()
        receiver_label = Label(receiver_frame, textvariable=self.receiver_status)
        self.receiver_status.set("")
        receiver_label.pack()
        self.listen_button = Button(receiver_frame, text='Start Listening', command=self.start_listening_for_connections)
        self.listen_button.pack(fill=X, expand=1)

        receiver_frame.pack(fill=BOTH)

    def start_listening_for_connections(self):
        host_ip = {v: k for k, v in self.all_ips.items()}[self.receiver_ip_box_value.get()]
        port = self.port_number_value.get()
        self.connection_receiver.start_listening(host_ip, port)
        self.listen_button.configure(text="Stop Listening", command=self.stop_listening_for_connections)

    def stop_listening_for_connections(self):
        self.connection_receiver.stop_listening()
        self.listen_button.configure(text='Start Listening', command=self.start_listening_for_connections)

    def receiver_status_callback(self, status):
        self.receiver_status.set(status)

if __name__ == '__main__':
    ft = FileTransfer()
    mainloop()
