#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import socket
import json
import argparse
import threading
from pathlib import Path
import uuid

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

root = tk.Tk()
root.title("Client")

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
    for i in "Connect", "Send", "Clear":
        b = tk.Button(master=frame, text=i)
        b.pack(side="left")
        yield b


b1, b2, b3 = buttons()


def print_system_notification(message):
    data = str(message)
    now = str(datetime.now())[:-7]
    text.insert("insert", "({}) : {}\n".format(now, data), 'notification')


class Client:
    client_id = ''
    host = '127.0.0.1'
    info = dict()
    port = 65432

    # Unique identifier for each client.
    uuid = uuid.uuid1()

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def set_address(self, host, port):
        self.host = host
        self.port = port

    def set_client_id(self, client_id):
        self.client_id = client_id

    def connect(self):
        now = str(datetime.now())[:-7]

        client_id = g_entry_client_id.get()
        if not client_id:
            print_system_notification("[err] client id = empty; please fill")
        else:
            try:
                self.s.connect((self.host, self.port))
                self.client_id = client_id
                text.insert("insert", "({}) : Connected.\n".format(now))
                msg = self.client_id
                self.s.sendall(bytes(msg.encode("utf-8")))
                self.receive()
            except ConnectionRefusedError:
                text.insert("insert", "({}) : The server is not online.\n".format(now))

    def disconnect(self):
        self.s.close()

    def handle_message(self, command):
        print_system_notification("[ID=" + self.client_id + "] received command from server =" + command)
        #Messages are received from clients here.

    def receive(self):
        status.configure(bg='green', text='Connected')
        while True:
            data = str(self.s.recv(1024))[2:-1]
            now = str(datetime.now())[:-7]
            if len(data) == 0:
                pass
            else:
                text.insert("insert", "({}) : {}\n".format(now, data), 'remote')
                self.handle_message(data)   

    # Retrieves the command written in the text and sends it to Server.
    def send(self):
        self.send_bytes_to_server(g_entry_msg.get())

    # Sends response to server.
    # It adds the client uuid based on which the server replies to client.
    # @Param response String to send to server.
    def send_bytes_to_server(self, msg_to_send):
        full_msg_to_send = "{} {}".format(self.client_id, msg_to_send)
        g_entry_msg.delete("0", "end")

        now = str(datetime.now())[:-7]
        try:
            self.s.sendall(bytes(full_msg_to_send.encode("utf-8")))
            text.insert("insert", "[info] ({}) : sent msg ({})\n".format(now, full_msg_to_send))
        except BrokenPipeError:
            text.insert("insert", "\n[err] Date: {}\Server has been disconnected.\n".format(now))
            self.s.close()


g_clients = list()


def search_client(client_id):
    for c in g_clients:
        if c[1] == client_id:
            return c[0]
    return None


def connect():
    client_id = g_entry_client_id.get()

    if not client_id:
        print_system_notification("[err] client id = empty; please fill")
    else:
        is_already_connected = True
        if search_client(client_id) is None:
            is_already_connected = False
        else:
            print_system_notification("[err] client " + client_id + " is already connected")

        if not is_already_connected:
            c1 = Client()
            c1.set_address(args.host, args.p)
            c1.set_client_id(client_id)

            tup = (c1, client_id)
            g_clients.append(tup)

            t1 = threading.Thread(target=c1.connect)
            t1.start()


def send():
    client_id = g_entry_client_id.get()
    c1 = search_client(client_id)
    if c1 is None:
        print_system_notification("[err] client " + client_id + " is not connected")
    else:
        t2 = threading.Thread(target=c1.send)
        t2.start()


def clear():
    text.delete("1.0", "end")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    b1.configure(command=connect)
    b2.configure(command=send)
    b3.configure(command=clear)

    t0 = threading.Thread(target=root.mainloop)
    t0.run()
