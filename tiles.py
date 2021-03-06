# encoding: utf-8
import random
import pyglet
from pyglet.window import key
from pyglet.gl import gl
from pyglet.gl import *
from ctypes import pointer

DYNAMIC_RENDERING = True
window = pyglet.window.Window()
fps_display = pyglet.clock.ClockDisplay(color=(.5, .8, .5, .5))

arrows = {"up": False, "down": False, "left": False, "right": False}

kitten_png = pyglet.resource.image('kitten.png')
kitten_png.anchor_x = kitten_png.width / 2
kitten_png.anchor_y = kitten_png.height / 2

flashlight_jpg = pyglet.resource.image('flashlight2.jpg')
flashlight_jpg.anchor_x = flashlight_jpg.width / 2
flashlight_jpg.anchor_y = flashlight_jpg.height / 2

flashlight_left = pyglet.sprite.Sprite(flashlight_jpg, blend_src=GL_ONE, blend_dest=GL_ONE)
flashlight_left.rotation = -10
flashlight_left.scale = 2

flashlight_right = pyglet.sprite.Sprite(flashlight_jpg, x=50, blend_src=GL_ONE, blend_dest=GL_ONE)
flashlight_right.rotation = 10
flashlight_right.scale = 2

class Spritesheet:
    def __init__(self, img_file, sprite_size):
        self.img = pyglet.resource.image(img_file)
        self.size = sprite_size

    def getSprite(self, n, x, y, batch):
        region = self.img.get_region((n * self.size) % self.img.width,
                                     (self.img.height - self.size) - ((n * self.size) // self.img.width) * self.size,
                                     self.size, self.size)
        region.anchor_x = region.width / 2
        region.anchor_y = region.height / 2
        return pyglet.sprite.Sprite(region, x, y, batch=batch)

class Tile:
    size = 32
    def __init__(self, x, y, createSpriteCallback):
        self.x = x
        self.y = y
        self.sprite = None
        self.createSpriteCallback = createSpriteCallback

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.drawables = []
        self.light_framebuffer = GLuint()
        self.light_texture = GLuint()

        self.w = window.width
        self.h = window.height

        # Create and activate the light framebuffer
        glGenFramebuffers(1, pointer(self.light_framebuffer))
        glBindFramebuffer(GL_FRAMEBUFFER, self.light_framebuffer)

        # Create a texture to render light into, activate it, initialize it and bind it as COLOR_ATTACHMENT0 on
        # the light framebuffer
        glGenTextures(1, pointer(self.light_texture))
        glBindTexture(GL_TEXTURE_2D, self.light_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.w, self.h, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.light_texture, 0)

        # Deactivate the light texture
        glBindTexture(GL_TEXTURE_2D, 0)

        # Check the new framebuffer status
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("glCheckFramebufferStatus: ", status)

        # Deactivate the light framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def resize(self, width, height):
        # Resize the light texture
        self.w = width
        self.h = height
        # Activate the light framebuffer and texture
        glBindFramebuffer(GL_FRAMEBUFFER, self.light_framebuffer)
        glBindTexture(GL_TEXTURE_2D, self.light_texture)

        # Resize the light texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.w, self.h, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

        # Deactivate the light framebuffer and texture
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def drawLighting(self):
        flashlight_left.draw()
        flashlight_right.draw()

    def drawLightBuffer(self):
        # Activate the light framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.light_framebuffer)

        # Enable 2D textures
        glEnable(GL_TEXTURE_2D)

        # Activate light texture
        glBindTexture(GL_TEXTURE_2D, self.light_texture)

        # Generate an AWESOME mipmap
        glGenerateMipmap(GL_TEXTURE_2D)

        # Deactivate colortex
        glBindTexture(GL_TEXTURE_2D, 0)

        # Create a viewport for rendering into the light framebuffer/texture and clear it
        glPushAttrib(GL_VIEWPORT_BIT | GL_ENABLE_BIT)
        glViewport(0, 0, self.w, self.h)
        glClearColor(0.03, 0.03, 0.03, 0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw the actual lighting
        self.drawLighting()

        # Pop the viewport
        glPopAttrib()

        # Dectivate the light framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Enable blending
        glEnable(GL_BLEND)

        # Activate the light texture
        glBindTexture(GL_TEXTURE_2D, self.light_texture)

        # Set the base color to white
        glColor4f(1, 1, 1, 1)

        # Load the identity matrix
        glPushMatrix()
        glLoadIdentity()

        # Draw a rectangle covering the screen, containing the light texture
        # Blend the background with the light color
        glBlendFunc(GL_ZERO, GL_SRC_COLOR)
        glBlendEquation(GL_FUNC_ADD)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(0, 1); glVertex2f(0, self.h)
        glTexCoord2f(1, 1); glVertex2f(self.w, self.h)
        glTexCoord2f(1, 0); glVertex2f(self.w, 0)
        glEnd()

        # Draw a rectangle covering the screen, containing the light texture
        # Blend add the light color to the background
        glBlendFunc(GL_ONE, GL_ONE)
        glBlendEquation(GL_FUNC_ADD)
        glColor4f(0.5, 0.5, 0.5, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(0, 1); glVertex2f(0, self.h)
        glTexCoord2f(1, 1); glVertex2f(self.w, self.h)
        glTexCoord2f(1, 0); glVertex2f(self.w, 0)
        glEnd()

        glPopMatrix()

        # Deactivate the light texture
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_BLEND)

    def draw(self):
        gl.glPushMatrix()
        gl.glTranslatef(int(-self.x + window.width / 2), int(-self.y + window.height / 2), 0)
        for drawable in self.drawables:
            drawable.draw()

        self.drawLightBuffer()

        glPopMatrix()

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
rows = 200
cols = 200
tiles_batch = pyglet.graphics.Batch()
for rownum in range(0, rows):
    row = []
    for colnum in range(0, cols):
        def tileClosure(tile_type, x, y):
            return lambda: grass_tiles.getSprite(tile_type, x, y, tiles_batch)
        x = colnum * grass_tiles.size - (cols / 2) * grass_tiles.size
        y = rownum * grass_tiles.size - (rows / 2) * grass_tiles.size
        row.append(Tile(colnum, rownum, tileClosure(random.randint(0, 8), x, y)))
        if not DYNAMIC_RENDERING:
            row[colnum].sprite = row[colnum].createSpriteCallback()

    tiles.append(row)
c.addDrawable(tiles_batch)

p = Player(0, 0)
c.addDrawable(p)

@window.event
def on_resize(width, height):
    c.resize(width, height)

@window.event
def on_draw():
    window.clear()
    c.x = p.x
    c.y = p.y
    c.draw()
    fps_display.draw()

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

active_tiles = {}

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

    flashlight_left.x = p.x - 60
    flashlight_left.y = p.y + 30
    flashlight_right.x = p.x + 60
    flashlight_right.y = p.y + 30

    if DYNAMIC_RENDERING:
        window_index_width = int(window.width // Tile.size)
        window_index_height = int(window.height // Tile.size)
        player_index_x = int(p.x // Tile.size)
        player_index_y = int(p.y // Tile.size)
        left_index = max(cols // 2 + player_index_x - window_index_width // 2, 0)
        right_index = min(cols // 2 + player_index_x + window_index_width // 2 + 2, cols - 1)
        bottom_index = max(rows // 2 + player_index_y - window_index_height // 2, 0)
        top_index = min(rows // 2 + player_index_y + window_index_height // 2 + 2, rows - 1)

        for x, y in active_tiles.keys():
            if x < left_index or x > right_index or y < bottom_index or y > top_index:
                tile = active_tiles[(x, y)]
                if tile.sprite:
                    tile.sprite.delete()
                    tile.sprite = None
                del active_tiles[(x, y)]

        for colnum in range(left_index, right_index):
            for rownum in range(bottom_index, top_index):
                tile = tiles[rownum][colnum]
                if tile.sprite is None:
                    tile.sprite = tile.createSpriteCallback()
                    active_tiles[(tile.x, tile.y)] = tile

pyglet.clock.schedule_interval(update, 1 / 30.0)   # Schemalägg funktionen "update" att köras 120 gånger i sekunden
pyglet.app.run()                                 # Let the games begin!