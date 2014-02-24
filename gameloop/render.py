from pyglet.gl import *

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.drawables = []
        self.window_width = 0
        self.window_height = 0

    def draw(self, window_width, window_height):
        glPushMatrix()
        glTranslatef(int(-self.x + window_width / 2), int(-self.y + window_height / 2), 0)
        for drawable in self.drawables:
            drawable.draw()
        glPopMatrix()
        self.window_width = window_width
        self.window_height = window_height

    def addDrawable(self, obj):
        self.drawables.append(obj)

    def removeDrawable(self, obj):
        self.drawables.remove(obj)

    def positionToAbsolute(self, x, y):
        return x-self.x - self.window_width / 2, y-self.y - self.window_height / 2