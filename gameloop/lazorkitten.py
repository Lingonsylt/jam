# encoding: utf-8
import json
import pyglet
import client
import network
import entity
import gamestate

class Lazorkitten(gamestate.Gamestate):
    def __init__(self, inputstate=None, camera=None):
        super(Lazorkitten, self).__init__(inputstate, camera)

        kitten = Kitten(0, 0, 0, 0)
        self.camera.addDrawable(kitten)
        self.kittens = {
            kitten.id: kitten
        }

    def update(self, dt, packet):
        for kitten in self.kittens.values():
            kitten.update(dt, self.inputstate)

        for kitten in self.kittens.values():
            packet.addCommand(KittenStateCommand(kitten))

kitten_png = pyglet.resource.image('kitten.png')
kitten_png.anchor_x = kitten_png.width / 2
kitten_png.anchor_y = kitten_png.height / 2
class Kitten(entity.Entity):
    speed = 500

    def __init__(self, player_id, x, y, rot, anim_name='default'):
        kitten_sprite = pyglet.sprite.Sprite(kitten_png)
        kitten_sprite.scale = 0.3
        self.animations = {
            'default': kitten_sprite
        }
        self.id = player_id

        super(Kitten, self).__init__(x, y, rot, anim_name)

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
    def deserialize(cls, data):
        data = json.loads(data)
        t = data['type']
        del data['type']
        data['kitten'] = Kitten.deserialize(data['kitten'])
        return network.server_commands[t](**data)
network.server_commands[KittenStateCommand.__name__] = KittenStateCommand

if __name__ == '__main__':
    c = client.Client(Lazorkitten)
    c.start()