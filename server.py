# encoding: utf-8
from _socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
from socket import socket
import threading
import time


def recv(sock):
    """
    Read a 4 byte header string and interpret it as a 4-digit zero-padded integer, the size of the coming message
    Four bytes of "0052" means a message of 52 bytes should be read
    Read all bytes specified by the header and return the message
    """
    length = int(sock.recv(4))
    msg = ''
    while len(msg) < length:
        chunk = sock.recv(length-len(msg))
        if chunk == '':
            raise RuntimeError("socket connection broken")
        msg = msg + chunk
    return msg


def listen():
    """
    Echo all messages back to client
    """
    addr = ("localhost", 6666)
    print "Listening to", addr
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind(addr)
    server.listen(5)
    c, caddr = server.accept()
    print "Accepted connection from", c
    while True:
        msg = recv(c)
        obj = json.loads(msg)
        if obj == "DIE!":
            return
        # time.sleep(0.1) Simulera lagg
        reply = json.dumps(obj)
        reply = "%04d%s" % (len(reply), reply)
        c.send(reply)


def startServerInThread():
    t = threading.Thread(target=listen)
    t.start()
    time.sleep(0.5)