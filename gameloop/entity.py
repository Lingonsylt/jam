import json

class Entity(object):
    animations = {}
    def __init__(self, x, y, rot, anim_name='default'):
        self.x = x
        self.y = y
        self.rot = rot
        self.anim_name = anim_name
        self.anim = self.animations[self.anim_name]

    def __unicode__(self):
        return u"%s(%s, %s, %s, ...)" % (self.__class__.__name__, self.x, self.y, self.rot)

    def update(self, dt, gamestate, inputstate, packet):
        pass

    def draw(self):
        self.anim.draw()

    def destroy(self):
        for anim in self.animations.values():
            anim.destroy()

    def serialize(self):
        return json.dumps({'x': self.x, 'y': self.y, 'anim_name': self.anim_name})

    @classmethod
    def deserialize(cls, data):
        return cls(**json.loads(data))

    def draw(self):
        self.anim.draw(self.x, self.y, self.rot)