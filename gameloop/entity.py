import json

class Animation:
    def __init__(self, createSprite):
        self.createSprite = createSprite
        self.sprite = None

    def draw(self, x, y, rot):
        if self.sprite is None:
            self.sprite = self.createSprite()
        self.sprite.x = x
        self.sprite.y = y
        self.sprite.rot = rot
        self.sprite.draw()

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
        self.anim.draw(self.x, self.y, self.rot)