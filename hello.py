import math
import pyglet
from pyglet.window import key
from pyglet.window import mouse

window = pyglet.window.Window()
# Logga alla event:
# window.push_handlers(pyglet.window.event.WindowEventLogger())

label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

kitten_png = pyglet.resource.image('kitten.png')
kitten_png.anchor_x = kitten_png.width / 2
kitten_png.anchor_y = kitten_png.height / 2
kitten = pyglet.sprite.Sprite(kitten_png, window.width / 2, window.height / 2)
kitten.scale = 0.3
kitten.speed = 500

lazor_png = pyglet.resource.image('lazor.png')
lazor_png.anchor_x = lazor_png.width / 2
lazor_png.anchor_y = lazor_png.height / 2


def get_lazor(x, y, rot):
    lazor = pyglet.sprite.Sprite(lazor_png, x, y)
    lazor.speed = 600
    lazor.rotation = rot
    lazor.scale = 0.6
    return lazor

lazors = []

arrows = {"up": False, "down": False, "left": False, "right": False}
mouse.x = 0
mouse.y = 0

@window.event
def on_draw():
    window.clear()
    kitten.draw()
    for lazor in lazors:
        lazor.draw()
    label.draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        lazors.append(get_lazor(kitten.x + (kitten.height / 2) * 0.5 * math.sin(kitten.rotation * (math.pi / 180)) +
                                (kitten.width / 2) * 0.2 * math.sin((kitten.rotation - 90) * (math.pi / 180)),
                                kitten.y + (kitten.height / 2) * 0.5 * math.cos(kitten.rotation * (math.pi / 180)) +
                                (kitten.width / 2) * 0.2 * math.cos((kitten.rotation - 90) * (math.pi / 180)), kitten.rotation))
        lazors.append(get_lazor(kitten.x + (kitten.height / 2) * 0.5 * math.sin(kitten.rotation * (math.pi / 180)) -
                                (kitten.width / 2) * 0.2 * math.sin((kitten.rotation - 90) * (math.pi / 180)),
                                kitten.y + (kitten.height / 2) * 0.5 * math.cos(kitten.rotation * (math.pi / 180)) -
                                (kitten.width / 2) * 0.2 * math.cos((kitten.rotation - 90) * (math.pi / 180)), kitten.rotation))


@window.event
def on_mouse_motion(x, y, dx, dy):
    mouse.x = x
    mouse.y = y


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


def update(dt):
    if arrows["up"]:
        kitten.y += kitten.speed * dt
    if arrows["down"]:
        kitten.y -= kitten.speed * dt
    if arrows["left"]:
        kitten.x -= kitten.speed * dt
    if arrows["right"]:
        kitten.x += kitten.speed * dt

    kitten.rotation = math.atan2(mouse.x - kitten.x, mouse.y - kitten.y) * 180 / math.pi
    delete_lazors = []
    for lazor in lazors:
        lazor.x += math.sin(lazor.rotation * (math.pi / 180)) * lazor.speed * dt
        lazor.y += math.cos(lazor.rotation * (math.pi / 180)) * lazor.speed * dt
        if lazor.x < 0 or lazor.x > window.width or lazor.y < 0 or lazor.y > window.height:
            delete_lazors.append(lazor)

    for lazor in delete_lazors:
        lazors.remove(lazor)


pyglet.clock.schedule_interval(update, 1/120.0)

pyglet.app.run()