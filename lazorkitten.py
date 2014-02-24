# encoding: utf-8
import json
import math
import pyglet
from gameloop import client
from gameloop import network
from gameloop import entity
from gameloop import gamestate

class Lazorkitten(gamestate.Gamestate):
    width = 800
    height = 600

    def __init__(self, clients=None, inputstate=None, camera=None):
        super(Lazorkitten, self).__init__(clients, inputstate, camera)
        self.kittens = {}
        self.lazors = {}
        self.next_lazor_id = 0

        self.servercommandrepo.addCommand(KittenStateCommand)
        self.servercommandrepo.addCommand(CreateKittenCommand)
        self.servercommandrepo.addCommand(CreateLazorCommand)
        self.servercommandrepo.addCommand(LazorStateCommand)
        self.servercommandrepo.addCommand(DestroyLazorCommand)

        hello_lazorkitten_label = pyglet.text.Label('Hello, lazorkitten!',
                                                    font_name='Times New Roman',
                                                    font_size=36,
                                                    x=0, y=0,
                                                    anchor_x='center', anchor_y='center')
        self.camera.addDrawable(hello_lazorkitten_label)

    def onNewClient(self, client, packet, client_packet):
        for kitten in self.kittens.values():
            client_packet.addCommand(CreateKittenCommand(kitten))

        kitten = Kitten(client.id, 0, 0, 0)
        self.kittens[kitten.id] = kitten
        packet.addCommand(CreateKittenCommand(kitten))

    def update(self, dt, packet):
        for client in self.clients.values():
            kitten = self.kittens[client.id]
            kitten.update(dt, self, client.inputstate, packet)
            for click in client.inputstate['clicks']:
                self.onClick(dt, packet, client, click)

        for lazor in self.lazors.values():
            lazor.update(dt, self, None, packet)

    def onClick(self, dt, packet, client, click):
        client_kitten = self.kittens[client.id]

        left_lazor = Lazor(self.next_lazor_id,
                      client_kitten.x + 20 *
                                        math.sin(client_kitten.rot * (math.pi / 180)) +
                      10 * math.sin((client_kitten.rot - 90) * (math.pi / 180)),
                      client_kitten.y + 20 *
                                        math.cos(client_kitten.rot * (math.pi / 180)) +
                      10 * math.cos((client_kitten.rot - 90) * (math.pi / 180)),
                      client_kitten.rot)
        self.next_lazor_id += 1
        self.lazors[left_lazor.id] = left_lazor
        packet.addCommand(CreateLazorCommand(left_lazor))

        right_lazor = Lazor(self.next_lazor_id,
                           client_kitten.x + 20 *
                                             math.sin(client_kitten.rot * (math.pi / 180)) -
                           10 * math.sin((client_kitten.rot - 90) * (math.pi / 180)),
                           client_kitten.y + 20 *
                                             math.cos(client_kitten.rot * (math.pi / 180)) -
                           10 * math.cos((client_kitten.rot - 90) * (math.pi / 180)),
                           client_kitten.rot)
        self.next_lazor_id += 1
        self.lazors[right_lazor.id] = right_lazor
        packet.addCommand(CreateLazorCommand(right_lazor))

class Kitten(entity.Entity):
    speed = 500

    def __init__(self, player_id, x, y, rot, anim_name='default'):
        def createSprite():
            kitten_png = pyglet.resource.image('kitten.png')
            kitten_png.anchor_x = kitten_png.width / 2
            kitten_png.anchor_y = kitten_png.height / 2

            kitten_sprite = pyglet.sprite.Sprite(kitten_png)
            kitten_sprite.scale = 0.3
            return kitten_sprite
        self.animations = {
            'default': entity.Animation(createSprite)
        }
        self.id = player_id

        super(Kitten, self).__init__(x, y, rot, anim_name)

    def __unicode__(self):
        return u"%s(%s, %s, %s, %s, ...)" % (self.__class__.__name__, self.id, self.x, self.y, self.rot)

    def update(self, dt, gamestate, inputstate, packet):
        if inputstate['keys']["up"]:
            self.y += self.speed * dt
        if inputstate['keys']["down"]:
            self.y -= self.speed * dt
        if inputstate['keys']["left"]:
            self.x -= self.speed * dt
        if inputstate['keys']["right"]:
            self.x += self.speed * dt

        self.rot = math.atan2(inputstate['mouse']['x'] - self.x, inputstate['mouse']['y'] - self.y) * 180 / math.pi

        packet.addCommand(KittenStateCommand(self))

    def serialize(self):
        return json.dumps({'player_id': self.id, 'x': self.x, 'y': self.y, 'rot': self.rot, 'anim_name': self.anim_name})

class Lazor(entity.Entity):
    speed = 600

    def __init__(self, lazor_id, x, y, rot, anim_name='default'):
        def createSprite():
            lazor_png = pyglet.resource.image('lazor.png')
            lazor_png.anchor_x = lazor_png.width / 2
            lazor_png.anchor_y = lazor_png.height / 2
            lazor_sprite = pyglet.sprite.Sprite(lazor_png)
            lazor_sprite.scale = 0.6
            return lazor_sprite

        self.animations = {
            'default': entity.Animation(createSprite)
        }
        self.id = lazor_id

        super(Lazor, self).__init__(x, y, rot, anim_name)

    def update(self, dt, gamestate, inputstate, packet):
        self.x += math.sin(self.rot * (math.pi / 180)) * self.speed * dt
        self.y += math.cos(self.rot * (math.pi / 180)) * self.speed * dt

        packet.addCommand(LazorStateCommand(self))

        if self.x < -gamestate.width / 2 or self.x > gamestate.width / 2 or self.y < -gamestate.height / 2 or self.y > gamestate.height / 2:
            del gamestate.lazors[self.id]
            packet.addCommand(DestroyLazorCommand(self))

    def serialize(self):
        return json.dumps({'lazor_id': self.id, 'x': self.x, 'y': self.y, 'rot': self.rot, 'anim_name': self.anim_name})

class KittenStateCommand(network.ServerCommand):
    def __init__(self, kitten):
        self.kitten = kitten

    def execute(self, gamestate):
        kitten = gamestate.kittens[self.kitten.id]
        kitten.x = self.kitten.x
        kitten.y = self.kitten.y
        kitten.rot = self.kitten.rot

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'kitten': self.kitten.serialize()})

    @classmethod
    def deserialize(cls, commands, data):
        data = json.loads(data)
        t = data['type']
        del data['type']
        data['kitten'] = Kitten.deserialize(data['kitten'])
        return commands[t](**data)

class CreateKittenCommand(network.ServerCommand):
    def __init__(self, kitten):
        self.kitten = kitten

    def execute(self, gamestate):
        gamestate.kittens[self.kitten.id] = self.kitten
        gamestate.camera.addDrawable(self.kitten)
        print "Created kitten with id ", self.kitten.id

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'kitten': self.kitten.serialize()})

    @classmethod
    def deserialize(cls, commands, data):
        data = json.loads(data)
        t = data['type']
        del data['type']
        data['kitten'] = Kitten.deserialize(data['kitten'])
        return commands[t](**data)

class LazorStateCommand(network.ServerCommand):
    def __init__(self, lazor):
        self.lazor = lazor

    def execute(self, gamestate):
        lazor = gamestate.lazors[self.lazor.id]
        lazor.x = self.lazor.x
        lazor.y = self.lazor.y
        lazor.rot = self.lazor.rot

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'lazor': self.lazor.serialize()})

    @classmethod
    def deserialize(cls, commands, data):
        data = json.loads(data)
        t = data['type']
        del data['type']
        data['lazor'] = Lazor.deserialize(data['lazor'])
        return commands[t](**data)

class CreateLazorCommand(network.ServerCommand):
    def __init__(self, lazor):
        self.lazor = lazor

    def execute(self, gamestate):
        gamestate.lazors[self.lazor.id] = self.lazor
        gamestate.camera.addDrawable(self.lazor)
        print "Created lazor with id ", self.lazor.id

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'lazor': self.lazor.serialize()})

    @classmethod
    def deserialize(cls, commands, data):
        data = json.loads(data)
        t = data['type']
        del data['type']
        data['lazor'] = Lazor.deserialize(data['lazor'])
        return commands[t](**data)

class DestroyLazorCommand(network.ServerCommand):
    def __init__(self, lazor):
        self.lazor = lazor

    def execute(self, gamestate):
        lazor = gamestate.lazors[self.lazor.id]
        del gamestate.lazors[self.lazor.id]
        gamestate.camera.removeDrawable(lazor)
        lazor.destroy()
        print "Removed lazor with id ", self.lazor.id

    def serialize(self):
        return json.dumps({'type': self.__class__.__name__, 'lazor': self.lazor.serialize()})

    @classmethod
    def deserialize(cls, commands, data):
        data = json.loads(data)
        t = data['type']
        del data['type']
        data['lazor'] = Lazor.deserialize(data['lazor'])
        return commands[t](**data)

if __name__ == '__main__':
    c = client.Client(Lazorkitten)
    c.start()