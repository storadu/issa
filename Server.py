#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from tkinter import ttk
import socket
import json
import argparse
import threading

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

root = tk.Tk()
root.title("Server")

text = tk.Text(master=root)
text.pack(expand=True, fill="both")
text.tag_config('remote', foreground="blue")
text.tag_config('notification', foreground="yellow", background='black')

g_label_client_id = tk.Label(text="client id:")
g_label_client_id.pack()

g_entry_client_id = tk.Entry(master=root)
g_entry_client_id.pack(expand=True, fill="x")

g_label_msg = tk.Label(text="message:")
g_label_msg.pack()

g_entry_msg = tk.Entry(master=root)
g_entry_msg.pack(expand=True, fill="x")

frame = tk.Frame(master=root)
frame.pack()

status = tk.Button(master=frame, text='Disconnected', bg='red')
status.pack(side="left")


def buttons():
    for i in "Send", "Clear":
        b = tk.Button(master=frame, text=i)
        b.pack(side="left")
        yield b


b1, b2 = buttons()


def print_system_notification(message):
    data = str(message)
    now = str(datetime.now())[:-7]
    text.insert("insert", "({}) : {}\n".format(now, data), 'notification')


class Server:

    host = '127.0.0.1'
    port = 65432
    clients = list()

    # Dictionary containing registered clients (phone or car).
    # It contains pairs of (unique identifier - phone IMEI or car number, client uuid).
    registered_clients = {}

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rental = []

    def set_address(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen(10)
        now = str(datetime.now())[:-7]
        text.insert("insert", "[info] ({}) : Started.\n".format(now))
        self.condition()

    def accept(self):
        c, addr = self.s.accept()
        data = c.recv(1024)
        tup = (c, data)
        self.clients.append(tup)
        status.configure(bg='green', text='Connected')
        # text.insert("insert", "({}) : {} connected.\n".format(str(datetime.now())[:-7], str(data)[1:]))

    # Parses messages received from clients.
    # @Param command Message received from client (phone app / car).
    def handle_message(self, command):
        #Messages are received from clients here. The structure of the message is client id + whitespace + message
        print_system_notification("received command from client =" + command)

        print_system_notification('handle_message end')

    def receive(self):
        for c in self.clients:

            def f():
                data = str(c[0].recv(1024))[2:-1]
                now = str(datetime.now())[:-7]
                if len(data) == 0:
                    pass
                else:
                    text.insert("insert", "({}) : {}\n".format(now, data), 'remote')
                    self.handle_message(data)

            t1_2_1 = threading.Thread(target=f)
            t1_2_1.start()

    def condition(self):
        while True:
            t1_1 = threading.Thread(target=self.accept)
            t1_1.daemon = True
            t1_1.start()
            t1_1.join(1)
            t1_2 = threading.Thread(target=self.receive)
            t1_2.daemon = True
            t1_2.start()
            t1_2.join(1)

    # Retrieves input from text box and sends request to client.
    # Will read from text boxes:
    # 1) client_id = unique identifier of the client who should receive the message
    # 2) msg_to_send = full text which should be sent by server to client
    def send(self):
        client_id = g_entry_client_id.get()
        msg_to_send = str(g_entry_msg.get())

        g_entry_client_id.delete("0", "end")
        g_entry_msg.delete("0", "end")

        if not msg_to_send or not client_id:
            print_system_notification("[err] client ID / msg to send is empty")
        else:
            self.send_bytes_to_client(client_id, msg_to_send)

    def send_bytes_to_client(self, client_id, msg_to_send):
        now = str(datetime.now())[:-7]

        try:
            msg_sent = False
            for c in self.clients:
                if c[1] == client_id.encode('utf-8'):
                    c[0].sendall(bytes(msg_to_send.encode("utf-8")))
                    text.insert("insert", "({}) : {}\n".format(now, msg_to_send))
                    msg_sent = True
            if not msg_sent:
                print_system_notification("msg was NOT sent to client \"" + client_id + "\"")
        except BrokenPipeError:
            text.insert("insert", "({}) : Client has been disconnected.\n".format(now))
            status.configure(bg='red', text='Disconnected')


g_s1 = Server()


def start():
    t1 = threading.Thread(target=g_s1.start)
    t1.start()


def send():
    t2 = threading.Thread(target=g_s1.send)
    t2.start()


def clear():
    text.delete("1.0", "end")


def destroy():
    root.destroy()
    exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-port', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    g_s1.set_address(args.host, args.port)
    start()

    b1.configure(command=send)
    b2.configure(command=clear)

    t0 = threading.Thread(target=root.mainloop)
    t0.run()
