import json
import socket
import sys
from _socket import AF_INET, SOCK_STREAM

def recv(sock):
    """
    Read a 4 byte header string and interpret it as a 4-digit zero-padded integer, the size of the coming message
    Four bytes of "0052" means a message of 52 bytes should be read
    Read all bytes specified by the header and return the message
    """
    try:
        length = int(sock.recv(4))
        msg = ''
        while len(msg) < length:
            chunk = sock.recv(length - len(msg))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            msg = msg + chunk
        return msg
    except socket.error, e:
        err = e.args[0]
        if err != socket.errno.EAGAIN and err != socket.errno.EWOULDBLOCK:
            raise
        return None

class Packet:
    def __init__(self, commands = None):
        self.commands = [] if commands is None else commands

    def addCommand(self, command):
        self.commands.append(command)

    def serialize(self):
        return json.dumps([command.serialize() for command in self.commands])

    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError("Use subclass ClientPacket och ServerPacket")

class CommandRepository(object):
    deserializer = None

    def __init__(self):
        self.commands = {}

    def addCommand(self, command_cls):
        self.commands[command_cls.__name__] = command_cls

    def deserialize(self, data):
        return Packet([self.deserializer.deserialize(self.commands, command) for command in json.loads(data)])

class ClientCommand:
    def execute(self, inputstate, onPress):
        pass

    def serialize(self):
        pass

    @classmethod
    def deserialize(cls, client_commands, data):
        data = json.loads(data)
        t = data['type']
        del data['type']
        return client_commands[t](**data)

class KeyboardStateCommand(ClientCommand):
    def __init__(self, keys):
        self.keys = keys

    def execute(self, inputstate, onPress):
        inputstate['keys'].update(self.keys)

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'keys': self.keys})

class InputPressCommand(ClientCommand):
    def __init__(self, buttons):
        self.buttons = buttons

    def execute(self, inputstate, onPress):
        for key in self.buttons:
            onPress(key)

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'buttons' : self.buttons})

class MouseStateCommand(ClientCommand):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def execute(self, inputstate, onPress):
        inputstate['mouse']['x'] = self.x
        inputstate['mouse']['y'] = self.y

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'x': self.x, 'y': self.y})

class KillServerCommand(ClientCommand):
    def execute(self, inputstate, onPress):
        sys.exit(0)

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__})

class ClientCommandRepository(CommandRepository):
    deserializer = ClientCommand

    def __init__(self):
        super(ClientCommandRepository, self).__init__()
        self.addCommand(KeyboardStateCommand)
        self.addCommand(InputPressCommand)
        self.addCommand(MouseStateCommand)
        self.addCommand(KeyboardStateCommand)
        self.addCommand(KillServerCommand)

class ServerCommand:
    def execute(self, gamestate):
        pass

    def serialize(self):
        pass

    @classmethod
    def deserialize(cls, server_commands, data):
        obj = json.loads(data)
        return server_commands[obj['type']].deserialize(server_commands, data)  # Decodes json a second time. Might be slow

class ServerCommandRepository(CommandRepository):
    deserializer = ServerCommand

class ClientNetworkState:
    def __init__(self, gamestate, commandrepo):
        self.gamestate = gamestate
        self.commandrepo = commandrepo
        self.createNewPacket(0, 0)

    def connect(self):
        addr = ("localhost", 6666)
        self.sock = socket.socket(AF_INET, SOCK_STREAM)
        self.sock.connect(addr)
        self.sock.setblocking(0)

    def createNewPacket(self, last_mouse_x, last_mouse_y):
        self.packet = Packet()
        self.keyboard_state = KeyboardStateCommand({})
        self.mouse_state = MouseStateCommand(last_mouse_x, last_mouse_y)
        self.packet.addCommand(self.keyboard_state)
        self.packet.addCommand(self.mouse_state)

    def send(self):
        msg = self.packet.serialize()
        msg = "%04d%s" % (len(msg), msg)
        self.sock.send(msg)
        self.createNewPacket(self.mouse_state.x, self.mouse_state.y)

    def recv(self):
        msg = recv(self.sock)
        if msg is not None:
            packet = self.commandrepo.deserialize(msg)
            for command in packet.commands:
                command.execute(self.gamestate)