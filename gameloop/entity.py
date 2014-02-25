class Entity(object):
    animations = {}
    def __init__(self, x, y, rot, anim_name='default'):
        super(Entity, self).__init__()  # Required for multiple-inheritance to call __init__ of all superclasses
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

    def draw(self):
        self.anim.draw(self.x, self.y, self.rot)

    @classmethod
    def deserialize(cls, dictobj):
        return cls(**dictobj)