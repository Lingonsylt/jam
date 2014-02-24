# encoding: utf-8
import json
import pyglet
from gameloop import client
from gameloop import network
from gameloop import entity
from gameloop import gamestate

class Lazorkitten(gamestate.Gamestate):
    def __init__(self, clients=None, inputstate=None, camera=None):
        super(Lazorkitten, self).__init__(clients, inputstate, camera)
        self.kittens = {}

        self.servercommandrepo.addCommand(KittenStateCommand)
        self.servercommandrepo.addCommand(CreateKittenCommand)

    def onNewClient(self, client, packet, client_packet):
        for kitten in self.kittens.values():
            client_packet.addCommand(CreateKittenCommand(kitten))

        kitten = Kitten(client.id, 0, 0, 0)
        self.kittens[kitten.id] = kitten
        packet.addCommand(CreateKittenCommand(kitten))

    def update(self, dt, packet):
        for kitten in self.kittens.values():
            kitten.update(dt, self.clients[kitten.id].inputstate)

        for kitten in self.kittens.values():
            packet.addCommand(KittenStateCommand(kitten))

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

    def update(self, dt, inputstate):
        if inputstate['keys']["up"]:
            self.y += self.speed * dt
        if inputstate['keys']["down"]:
            self.y -= self.speed * dt
        if inputstate['keys']["left"]:
            self.x -= self.speed * dt
        if inputstate['keys']["right"]:
            self.x += self.speed * dt

    def serialize(self):
        return json.dumps({'player_id': self.id, 'x': self.x, 'y': self.y, 'rot': self.rot, 'anim_name': self.anim_name})

lazor_png = pyglet.resource.image('lazor.png')
lazor_png.anchor_x = lazor_png.width / 2
lazor_png.anchor_y = lazor_png.height / 2
class Lazor(entity.Entity):
    speed = 600

    def __init__(self, lazor_id, x, y, rot, anim_name='default'):
        lazor_sprite = pyglet.sprite.Sprite(lazor_png)
        lazor_sprite.scale = 0.6
        self.animations = {
            'default': lazor_sprite
        }
        self.id = lazor_id

        super(Lazor, self).__init__(x, y, rot, anim_name)

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

if __name__ == '__main__':
    c = client.Client(Lazorkitten)
    c.start()