# encoding: utf-8
from _socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import pprint
from socket import socket
import threading
import time
import sys
import network
import pyglet

class Server:
    def __init__(self, gamestate_cls):
        self.inputstate = {'keys': {"up": False, "down": False, "left": False, "right": False}, 'mouse': {'x': 0, 'y': 0}}
        self.gamestate = gamestate_cls(inputstate=self.inputstate)
        self.clients = []

    def recv(self, sock):
        return network.recv(sock)

    def update(self, dt):
        self.read()
        packet = network.Packet()
        self.gamestate.update(dt, packet)
        serialized_packet = packet.serialize()
        for conn in self.clients:
            self.send(conn, serialized_packet)

    def send(self, conn, msg):
        msg = "%04d%s" % (len(msg), msg)
        conn.send(msg)

    def listen(self):
        addr = ("localhost", 6666)
        print "Listening to", addr
        server = socket(AF_INET, SOCK_STREAM)
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server.bind(addr)
        server.listen(5)
        conn, caddr = server.accept()
        self.clients.append(conn)
        conn.setblocking(0)
        print "Accepted connection from", conn
        pyglet.clock.schedule_interval(self.update, 1 / 30.0)


    def read(self):
        for conn in self.clients:
            msg = self.recv(conn)
            if msg is not None:
                packet = network.ClientPacket.deserialize(msg)
                for command in packet.commands:
                    command.execute(self.inputstate, lambda x: sys.stdout.write("%s\n" % x))
                #pprint.pprint(self.inputstate)

    def startInThread(self):
        t = threading.Thread(target=self.listen)
        t.start()
        time.sleep(0.5)

    def start(self):
        self.listen()
        pyglet.app.run()
