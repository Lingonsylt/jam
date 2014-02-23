import json
import pyglet

class Entity(object):
    animations = {}
    def __init__(self, x, y, rot, anim_name='default'):
        self.x = x
        self.y = y
        self.rot = rot
        self.anim_name = anim_name
        self.anim = self.animations[self.anim_name]

    def update(self, dt, inputstate):
        pass

    def draw(self):
        self.anim.draw()

    def serialize(self):
        return json.dumps({'x': self.x, 'y': self.y, 'anim_name': self.anim_name})

    @classmethod
    def deserialize(cls, data):
        return cls(**json.loads(data))

    def draw(self):
        self.anim.x = self.x
        self.anim.y = self.y
        self.anim.rot = self.rot
        self.anim.draw()

kitten_png = pyglet.resource.image('kitten.png')
kitten_png.anchor_x = kitten_png.width / 2
kitten_png.anchor_y = kitten_png.height / 2
class Player(Entity):
    speed = 500

    def __init__(self, player_id, x, y, rot, anim_name='default'):
        kitten_sprite = pyglet.sprite.Sprite(kitten_png)
        kitten_sprite.scale = 0.3
        self.animations = {
            'default': kitten_sprite
        }
        self.id = player_id

        super(Player, self).__init__(x, y, rot, anim_name)

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
class Lazor(Entity):
    speed = 600
    animations = {
        'default': pyglet.sprite.Sprite(lazor_png)
    }