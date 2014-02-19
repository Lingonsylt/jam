# encoding: utf-8
import random
import pyglet
from pyglet.window import key
from pyglet.gl import gl
import math

window = pyglet.window.Window()

arrows = {"up": False, "down": False, "left": False, "right": False}

kitten_png = pyglet.resource.image('kitten.png')
kitten_png.anchor_x = kitten_png.width / 2
kitten_png.anchor_y = kitten_png.height / 2

class Spritesheet:
    def __init__(self, img_file, sprite_size):
        self.img = pyglet.resource.image(img_file)
        self.size = sprite_size

    def getSprite(self, n, x, y):
        region = self.img.get_region((n * self.size) % self.img.width,
                                     (self.img.height - self.size) - ((n * self.size) // self.img.width) * self.size,
                                     self.size, self.size)
        region.anchor_x = region.width / 2
        region.anchor_y = region.height / 2
        return pyglet.sprite.Sprite(region, x, y)

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.drawables = []

    def draw(self):
        gl.glPushMatrix()
        gl.glTranslatef(-self.x + window.width / 2, -self.y + window.height / 2, 0)
        for drawable in self.drawables:
            drawable.draw()

        gl.glPopMatrix()

    def addDrawable(self, obj):
        self.drawables.append(obj)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.s = pyglet.sprite.Sprite(kitten_png, x, y)
        self.s.scale = 0.3
        self.speed = 500

    def draw(self):
        self.s.x = self.x
        self.s.y = self.y
        self.s.draw()

grass_tiles = Spritesheet("gras_tiles.png", 32)
c = Camera(0, 0)

tiles = []
rows = 10
cols = 10
for rownum in range(0, rows):
    row = []
    for colnum in range(0, cols):
        tile = grass_tiles.getSprite(random.randint(0, 8), colnum * grass_tiles.size - (cols / 2) * grass_tiles.size, rownum * grass_tiles.size - (rows / 2) * grass_tiles.size)
        c.addDrawable(tile)
        row.append(tile)
    tiles.append(row)

p = Player(0, 0)
c.addDrawable(p)


@window.event
def on_draw():
    window.clear()
    c.x = p.x
    c.y = p.y
    c.draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.W:
        arrows["up"] = True
    elif symbol == key.S:
        arrows["down"] = True
    elif symbol == key.A:
        arrows["left"] = True
    elif symbol == key.D:
        arrows["right"] = True

@window.event
def on_key_release(symbol, modifiers):
    if symbol == key.W:
        arrows["up"] = False
    elif symbol == key.S:
        arrows["down"] = False
    elif symbol == key.A:
        arrows["left"] = False
    elif symbol == key.D:
        arrows["right"] = False

def update(dt):  # Körs 120 gånger per skund, schemaläggs med pyglet.clock.schedule_interval() under denna funktion
    # Flytta katten kitten.speed gånger delta time i de riktningar som knapparna är nedtryckta
    if arrows["up"]:
        p.y += p.speed * dt
    if arrows["down"]:
        p.y -= p.speed * dt
    if arrows["left"]:
        p.x -= p.speed * dt
    if arrows["right"]:
        p.x += p.speed * dt

pyglet.clock.schedule_interval(update, 1/120.0)  # Schemalägg funktionen "update" att köras 120 gånger i sekunden
pyglet.app.run()                                 # Let the games begin!