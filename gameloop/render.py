from pyglet.gl import *

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.drawables = []

    def draw(self, window_width, window_height):
        glPushMatrix()
        glTranslatef(int(-self.x + window_width / 2), int(-self.y + window_height / 2), 0)
        for drawable in self.drawables:
            drawable.draw()
        glPopMatrix()

    def addDrawable(self, obj):
        self.drawables.append(obj)