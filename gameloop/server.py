# encoding: utf-8
from _socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from socket import socket
import threading
import time
import network
import pyglet

class Client:
    def __init__(self, client_id, conn):
        self.id = client_id
        self.conn = conn
        self.inputstate = {'keys': {"up": False, "down": False, "left": False, "right": False},
                           'mouse': {'x': 0, 'y': 0}, 'presses': [], 'clicks': []}

class Server:
    def __init__(self, gamestate_cls):
        self.next_client_id = 0
        self.clients = {}
        self.gamestate = gamestate_cls(clients=self.clients)
        self.sock = None

    def recv(self, sock):
        return network.recv(sock)

    def update(self, dt):
        packet = network.Packet()
        self.accept(packet)
        self.read()
        self.gamestate.update(dt, packet)
        self.gamestate._updateNetworkedEntities(dt, packet)
        serialized_packet = network.Serializer.serialize(packet)
        for client in self.clients.values():
            self.send(client.conn, serialized_packet)
            client.inputstate['presses'] = []
            client.inputstate['clicks'] = []

    def send(self, conn, msg):
        msg = "%04d%s" % (len(msg), msg)
        conn.send(msg)

    def accept(self, packet):
        conn, caddr = network.accept(self.sock)
        if conn:
            client = Client(self.next_client_id, conn)
            self.next_client_id += 1
            self.clients[client.id] = client
            print "Accepted connection from client", client.id
            conn.setblocking(0)
            client_packet = network.Packet()
            self.gamestate._onNewClient(client, packet, client_packet)
            self.gamestate.onNewClient(client, packet, client_packet)
            self.send(conn, network.Serializer.serialize(client_packet))

    def listen(self, block_first_accept=False):
        addr = ("localhost", 6666)
        print "Listening to", addr
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(addr)
        self.sock.listen(5)
        if block_first_accept:
            packet = network.Packet()
            self.accept(packet)
            self.send(self.clients[self.clients.keys()[0]].conn, network.Serializer.serialize(packet))
        self.sock.setblocking(0)

        pyglet.clock.schedule_interval(self.update, 1 / 30.0)

    def read(self):
        for client in self.clients.values():
            msg = True
            while msg:
                msg = self.recv(client.conn)
                if msg is not None:
                    packet = network.Serializer.deserialize(msg)
                    for command in packet.commands:
                        command.execute(client.inputstate)


    def startInThread(self):
        t = threading.Thread(target=self.listen, args=(True,))
        t.start()
        time.sleep(0.5)

    def start(self):
        self.listen()
        pyglet.app.run()
