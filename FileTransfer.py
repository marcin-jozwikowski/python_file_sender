from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from ConnectionReceiver import ConnectionReceiver
from ConnectionSender import ConnectionSender
import os


class FileTransfer(object):

    connection_receiver = None
    all_ips = {}

    def __init__(self):
        self.connection_receiver = ConnectionReceiver()
        self.connection_receiver.set_status_callback(self.receiver_status_callback)
        self.all_ips = self.connection_receiver.get_all_ips()
        self.connection_sender = ConnectionSender()
        self.connection_sender.set_status_callback(self.sender_status_callback)

        self.top = Tk()

        # Whole receiver frame
        receiver_frame = Frame(self.top)
        # Main label
        receiver_label = Label(receiver_frame, text='Receiver', font=('Halvetica', 12, 'bold'))
        receiver_label.pack()

        # SelectBox + port input in one Frame
        receiver_ips_selector = Frame(receiver_frame)
        self.receiver_port_number_value = StringVar()
        self.receiver_port_number_value.set(self.connection_receiver.get_port())
        port_number = Entry(receiver_ips_selector, textvariable=self.receiver_port_number_value)
        port_number.pack(side=RIGHT)
        self.receiver_ip_box_value = StringVar()
        receiver_ip_box = Combobox(receiver_ips_selector, textvariable=self.receiver_ip_box_value)
        receiver_ip_box['values'] = list(self.all_ips.values())
        receiver_ip_box.current(0)
        receiver_ip_box.pack(side=LEFT, fill=BOTH, expand=1)
        receiver_ips_selector.pack(fill=BOTH, expand=1)

        # receiver status label
        self.receiver_status = StringVar()
        receiver_status_label = Label(receiver_frame, textvariable=self.receiver_status)
        self.receiver_status.set("Idle")
        receiver_status_label.pack()

        # main control button
        self.listen_button = Button(receiver_frame, text='Start Listening', command=self.start_listening_for_connections)
        self.listen_button.pack(fill=X, expand=1)

        # end of receiver frame
        receiver_frame.pack(fill=BOTH)

        # main sender frame
        sender_frame = Frame(self.top)
        # main label
        sender_label = Label(sender_frame, text='Sender', font=('Halvetica', 12, 'bold'))
        sender_label.pack()
        self.sender_status = StringVar()
        self.sender_ip_box_value = StringVar()
        self.sender_ip_box_value.set(self.get_single_host_ip(list(self.all_ips.values())[0]))
        self.sender_port_box_value = StringVar()
        self.sender_port_box_value.set(self.connection_sender.get_port())

        # sender IP input + port input
        sender_ip_selector_frame = Frame(sender_frame)
        sender_ip_entry = Entry(sender_ip_selector_frame, textvariable=self.sender_ip_box_value)
        sender_ip_entry.pack(side=LEFT, fill=BOTH, expand=1)
        sender_port_entry = Entry(sender_ip_selector_frame, textvariable=self.sender_port_box_value)
        sender_port_entry.pack(side=RIGHT)
        sender_ip_selector_frame.pack(fill=BOTH)

        # sender status label
        self.sender_status = StringVar()
        self.sender_status_label = Label(sender_frame, textvariable=self.sender_status)
        self.sender_status.set("Idle")
        self.sender_status_label.pack()

        choose_file_button = Button(sender_frame, text='Choose File', command=self.choose_file)
        choose_file_button.pack(fill=X, expand=1)

        # sender status label
        self.sent_file_path = StringVar()
        sent_file_path_label = Label(sender_frame, textvariable=self.sent_file_path)
        self.sent_file_path.set("")
        sent_file_path_label.pack()

        self.send_button = Button(sender_frame, text='Send', command=self.send_files)
        self.send_button.pack(fill=X, expand=1)
        sender_frame.pack(fill=BOTH)

        self.top.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def choose_file(self):
        file_path = filedialog.askopenfilename()
        self.sent_file_path.set(file_path)

    def get_single_host_ip(self, index):
        return {v: k for k, v in self.all_ips.items()}[index]

    def start_listening_for_connections(self):
        host_ip = self.get_single_host_ip(self.receiver_ip_box_value.get())
        port = self.receiver_port_number_value.get()
        self.connection_receiver.start_listening(host_ip, port)
        self.listen_button.configure(text="Stop Listening", command=self.stop_listening_for_connections)

    def stop_listening_for_connections(self):
        self.connection_receiver.stop_listening()
        self.listen_button.configure(text='Start Listening', command=self.start_listening_for_connections)

    def receiver_status_callback(self, status):
        self.receiver_status.set(status)

    def sender_status_callback(self, status):
        self.sender_status.set(status)
        self.sender_status_label.update()

    def send_files(self):
        path = self.sent_file_path.get()
        if os.path.isfile(path):
            host_ip = self.sender_ip_box_value.get()
            port = self.sender_port_box_value.get()
            try:
                self.connection_sender.send_file(file_path=path, host=host_ip, port=port)
            except ConnectionRefusedError:
                messagebox.showerror("Error", "Could not connect")
            except:
                messagebox.showerror("Error", "Could not send")
        else:
            messagebox.showerror("Error", "No file selected for sending")

    def on_window_close(self):
        self.stop_listening_for_connections()
        self.top.quit()


if __name__ == '__main__':
    ft = FileTransfer()
    mainloop()
