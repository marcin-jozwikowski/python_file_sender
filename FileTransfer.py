from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from ConnectionReceiver import ConnectionReceiver
from ConnectionSender import ConnectionSender
from queue import Queue
import os


class FileTransfer(object):

    connection_receiver = None
    all_ips = {}
    files_to_send = Queue()

    def __init__(self):
        self._is_sending = False
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

        choose_file_button = Button(sender_frame, text='Add File', command=self.add_file)
        choose_file_button.pack(side=LEFT, fill=BOTH, expand=1)
        choose_directory_button = Button(sender_frame, text='Add Directory', command=self.add_directory)
        choose_directory_button.pack(side=RIGHT, fill=BOTH, expand=1)
        sender_frame.pack(fill=BOTH)

        # sender status label
        send_button_frame = Frame(self.top)
        self.sent_file_label_value = StringVar()
        sent_file_path_label = Label(send_button_frame, textvariable=self.sent_file_label_value)
        self.sent_file_label_value.set("")
        sent_file_path_label.pack()

        self.send_button = Button(send_button_frame, text='Send', command=self.send_files)
        self.send_button.pack(fill=X, expand=1)
        send_button_frame.pack(fill=BOTH)

        self.top.protocol("WM_DELETE_WINDOW", self.on_window_close)

    #chose file button callback
    def add_file(self):
        file_path = filedialog.askopenfilename()
        file_name = os.path.basename(file_path)
        self._add_file_to_send(file_path, file_name)

    def _add_file_to_send(self, file_path, file_name):
        self.files_to_send.put({'path': file_path, 'name': file_name})
        self.update_sent_file_label()

    def add_directory(self):
        directory_path = filedialog.askdirectory(title="Select A Directory", mustexist=1)
        if directory_path is not None:
            self.parse_directory(os.path.dirname(directory_path), os.path.basename(directory_path))

    def parse_directory(self, base_directory, sub_directory=""):
        directory_path = os.path.join(base_directory, sub_directory)
        for file in os.listdir(directory_path):
            if os.path.isfile(os.path.join(directory_path, file)):
                self._add_file_to_send(file_path=os.path.join(directory_path, file), file_name=os.path.join(sub_directory, file))
            else:
                new_subdirectory = os.path.join(sub_directory, file)
                self.parse_directory(base_directory, new_subdirectory)

    def update_sent_file_label(self):
        self.sent_file_label_value.set("Files to send " + str(self.files_to_send.qsize()))

    #get host IP based on index of selected item
    def get_single_host_ip(self, index):
        return {v: k for k, v in self.all_ips.items()}[index]

    #start listening for connections on connection_receiver - butotn callback
    def start_listening_for_connections(self):
        host_ip = self.get_single_host_ip(self.receiver_ip_box_value.get())
        port = self.receiver_port_number_value.get()
        self.connection_receiver.start_listening(host_ip, port)
        self.listen_button.configure(text="Stop Listening", command=self.stop_listening_for_connections)

    #stop listening for connections - button callback
    def stop_listening_for_connections(self):
        self.connection_receiver.stop_listening()
        self.listen_button.configure(text='Start Listening', command=self.start_listening_for_connections)

    #callback for status change
    def receiver_status_callback(self, status):
        self.receiver_status.set(status)

    #callback for status change
    def sender_status_callback(self, status):
        self.sender_status.set(status)
        self.sender_status_label.update()

    def send_files(self):
        if not self._is_sending:  # if is not sending already
            self._is_sending = True
            host_ip = self.sender_ip_box_value.get()
            port = self.sender_port_box_value.get()
            while True:  # start sending in an infinite loop
                if self.files_to_send.qsize() > 0:  # if there is anything to send
                    file_to_send = self.files_to_send.get()  # get next file in queue
                    self.update_sent_file_label()
                    try:
                        # send the file
                        self.connection_sender.send_file(file_path=file_to_send['path'], file_name=file_to_send['name'],
                                                         host=host_ip, port=port)
                    except ConnectionRefusedError:
                        messagebox.showerror("Error", "Could not connect")
                    except:
                        messagebox.showerror("Error", "Could not send")
                else:
                    break  # no files left to send - breaking the loop
            self._is_sending = False  # done sending

    def on_window_close(self):
        self.stop_listening_for_connections()
        self.top.quit()


if __name__ == '__main__':
    ft = FileTransfer()
    mainloop()
