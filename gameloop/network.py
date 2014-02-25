import inspect
import json
import socket
import sys
from _socket import AF_INET, SOCK_STREAM
from gameloop import entity

class Serializer(object):
    def __init__(self):
        self.types = {}

    def addType(self, t):
        self.types[t.__name__] = t

    def _deserialize(self, data):
        return self._deserializeObject(json.loads(data))

    def _deserializeObject(self, obj):
        return self.types[obj['serialized_type']].deserialize(obj['payload'])

    @classmethod
    def deserialize(cls, data):
        return globals()['__serializer']._deserialize(data)

    @classmethod
    def deserializeObject(cls, obj):
        return globals()['__serializer']._deserializeObject(obj)

    @classmethod
    def getSerializable(cls, obj):
        return {'serialized_type': obj.__class__.__name__, 'payload': obj.getSerializable()}

    @classmethod
    def serialize(cls, obj):
        return globals()['__serializer']._serialize(obj)

    def _serialize(self, obj):
        return json.dumps(self.getSerializable(obj))

    class Serializable(object):
        _args = None

        def __init__(self):
            if self.__class__._args is None:
                args = inspect.getargspec(self.__init__)[0]
                args.remove('self')
                self.__class__._args = args

        @classmethod
        def deserialize(cls, dictobj):
            dictobj = {key: cls._getDeserialized(value) for key, value in dictobj.items()}
            return cls(**dictobj)

        @classmethod
        def _getDeserialized(cls, obj):
            if isinstance(obj, dict) and 'serialized_type' in obj:
                return Serializer.deserializeObject(obj)
            elif isinstance(obj, dict):
                return {key: cls._getDeserialized(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [cls._getDeserialized(item) for item in obj]
            else:
                return obj

        def getSerializable(self):
            if self._args is None:
                raise Exception("Subclass of Serializer.Serializable must call super(%s, self).__init__()!" %
                                self.__class__.__name__)
            dictobj = {serializable: getattr(self, serializable)
                       for serializable in self._args}
            for key, value in dictobj.items():
                dictobj[key] = self._getSerializable(value)

            return dictobj

        def _getSerializable(self, obj):
            if hasattr(obj, "getSerializable"):
                return Serializer.getSerializable(obj)
            elif isinstance(obj, dict):
                return {key: self._getSerializable(value) for key, value in obj.items()}

            elif isinstance(obj, list):
                return [self._getSerializable(item) for item in obj]
            else:
                return obj

if '__serializer' not in globals():
    globals()['__serializer'] = Serializer()

def serializable(cls):
    if not hasattr(cls, 'getSerializable'):
        raise NotImplementedError("serializable class must implement getSerializable")
    globals()['__serializer'].addType(cls)
    return cls

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

def accept(sock):
    try:
        return sock.accept()
    except socket.error, e:
        err = e.args[0]
        if err != socket.errno.EWOULDBLOCK:
            raise
        return None, None

@serializable
class Packet(Serializer.Serializable):
    def __init__(self, commands=None):
        super(Packet, self).__init__()
        self.commands = [] if commands is None else commands

    def addCommand(self, command):
        self.commands.append(command)

class ClientCommand(Serializer.Serializable):
    def execute(self, inputstate):
        pass

@serializable
class KeyboardStateCommand(ClientCommand):
    def __init__(self, keys):
        super(KeyboardStateCommand, self).__init__()
        self.keys = keys

    def execute(self, inputstate):
        inputstate['keys'].update(self.keys)

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'keys': self.keys})

@serializable
class InputPressCommand(ClientCommand):
    def __init__(self, buttons):
        super(InputPressCommand, self).__init__()
        self.buttons = buttons

    def execute(self, inputstate):
        for key in self.buttons:
            inputstate['pressed'].append(key)

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'buttons': self.buttons})

@serializable
class MouseClickCommand(ClientCommand):
    def __init__(self, button, x, y):
        super(MouseClickCommand, self).__init__()
        self.button = button
        self.x = x
        self.y = y

    def execute(self, inputstate):
        inputstate['clicks'].append(self)

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'button': self.button, 'x': self.x, 'y': self.y})

@serializable
class MouseStateCommand(ClientCommand):
    def __init__(self, x, y):
        super(MouseStateCommand, self).__init__()
        self.x = x
        self.y = y

    def execute(self, inputstate):
        inputstate['mouse']['x'] = self.x
        inputstate['mouse']['y'] = self.y

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'x': self.x, 'y': self.y})

@serializable
class KillServerCommand(ClientCommand):
    def execute(self, inputstate):
        sys.exit(0)

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__})

class ServerCommand(Serializer.Serializable):
    def execute(self, gamestate):
        pass

class NetworkedEntityCommand(ServerCommand):
    def __init__(self, entity):
        super(NetworkedEntityCommand, self).__init__()
        self.entity = entity

@serializable
class CreateNetworkedEntityCommand(NetworkedEntityCommand):
    def execute(self, gamestate):
        gamestate._networked_entities[self.entity.id] = self.entity
        gamestate.camera.addDrawable(self.entity)

@serializable
class UpdateNetworkedEntityCommand(NetworkedEntityCommand):
    def execute(self, gamestate):
        gamestate._networked_entities[self.entity.id].updateFromEntity(self.entity)

class ClientNetworkState:
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.createNewPacket(0, 0)

    def connect(self):
        addr = ("localhost", 6666)
        self.sock = socket.socket(AF_INET, SOCK_STREAM)
        try:
            self.sock.connect(addr)
        except socket.error, e:
            err = e.args[0]
            if err != socket.errno.ECONNREFUSED:
                raise
            return False

        self.sock.setblocking(0)
        return True

    def createNewPacket(self, last_mouse_x, last_mouse_y):
        self.packet = Packet()
        self.keyboard_state = KeyboardStateCommand({})
        self.mouse_state = MouseStateCommand(last_mouse_x, last_mouse_y)
        self.packet.addCommand(self.keyboard_state)
        self.packet.addCommand(self.mouse_state)

    def send(self):
        msg = Serializer.serialize(self.packet)
        msg = "%04d%s" % (len(msg), msg)
        self.sock.send(msg)
        self.createNewPacket(self.mouse_state.x, self.mouse_state.y)

    def recv(self):
        msg = True
        while msg:
            msg = recv(self.sock)
            if msg is not None:
                packet = Serializer.deserialize(msg)
                for command in packet.commands:
                    command.execute(self.gamestate)

class NetworkedEntity(entity.Entity, Serializer.Serializable):
    __args = None
    def __init__(self, client_id, id, x, y, rot, anim_name='default'):
        super(NetworkedEntity, self).__init__(x, y, rot, anim_name)
        self.id = id
        self.client_id = client_id

    @classmethod
    def create(cls, obj, gamestate, packet):
        if not isinstance(obj, NetworkedEntity):
            raise Exception("obj must be a subclass of NetworkedEntity!")
        obj.id = gamestate._networked_entity_id_next
        gamestate._networked_entities[obj.id] = obj
        gamestate._networked_entity_id_next += 1
        packet.addCommand(CreateNetworkedEntityCommand(obj))

    def updateFromEntity(self, entity):
        for arg in self._args:
            setattr(self, arg, getattr(entity, arg))