import json

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