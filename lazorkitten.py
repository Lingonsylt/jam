# encoding: utf-8
import math
import pyglet
from gameloop import client, render, network, entity, gamestate
from gameloop.network import serializable

class Lazorkitten(gamestate.Gamestate):
    width = 800
    height = 600

    def __init__(self, clients=None, inputstate=None, camera=None):
        super(Lazorkitten, self).__init__(clients, inputstate, camera)
        self.kittens = {}
        self.lazors = {}
        self.next_lazor_id = 0
        hello_lazorkitten_label = pyglet.text.Label('Hello, lazorkitten!',
                                                    font_name='Times New Roman',
                                                    font_size=36,
                                                    x=0, y=0,
                                                    anchor_x='center', anchor_y='center')
        self.camera.addDrawable(hello_lazorkitten_label)

    def onNewClient(self, client, packet, client_packet):
        kitten = Kitten(client.id, None, 0, 0, 0)
        network.NetworkedEntity.create(kitten, self, packet)
        self.kittens[kitten.client_id] = kitten

    def update(self, dt, packet):
        for client in self.clients.values():
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

@serializable
class Kitten(network.NetworkedEntity):
    speed = 500

    def __init__(self, client_id, id, x, y, rot, anim_name='default'):
        def createSprite():
            kitten_png = pyglet.resource.image('kitten.png')
            kitten_png.anchor_x = kitten_png.width / 2
            kitten_png.anchor_y = kitten_png.height / 2

            kitten_sprite = pyglet.sprite.Sprite(kitten_png)
            kitten_sprite.scale = 0.3
            return kitten_sprite
        self.animations = {
            'default': render.Animation(createSprite)
        }

        super(Kitten, self).__init__(client_id, id, x, y, rot, anim_name)

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

@serializable
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
            'default': render.Animation(createSprite)
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

    def getSerializable(self):
        return {'lazor_id': self.id, 'x': self.x, 'y': self.y, 'rot': self.rot, 'anim_name': self.anim_name}

@serializable
class LazorStateCommand(network.ServerCommand):
    def __init__(self, lazor):
        super(LazorStateCommand, self).__init__()
        self.lazor = lazor

    def execute(self, gamestate):
        lazor = gamestate.lazors[self.lazor.id]
        lazor.x = self.lazor.x
        lazor.y = self.lazor.y
        lazor.rot = self.lazor.rot

@serializable
class CreateLazorCommand(network.ServerCommand):
    def __init__(self, lazor):
        super(CreateLazorCommand, self).__init__()
        self.lazor = lazor

    def execute(self, gamestate):
        gamestate.lazors[self.lazor.id] = self.lazor
        gamestate.camera.addDrawable(self.lazor)
        print "Created lazor with id ", self.lazor.id

@serializable
class DestroyLazorCommand(network.ServerCommand):
    def __init__(self, lazor):
        super(DestroyLazorCommand, self).__init__()
        self.lazor = lazor

    def execute(self, gamestate):
        lazor = gamestate.lazors[self.lazor.id]
        del gamestate.lazors[self.lazor.id]
        gamestate.camera.removeDrawable(lazor)
        lazor.destroy()
        print "Removed lazor with id ", self.lazor.id

if __name__ == '__main__':
    c = client.Client(Lazorkitten)
    c.start()