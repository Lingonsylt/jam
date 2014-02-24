import pyglet
from pyglet.window import key
import animation_loader

window = pyglet.window.Window()

class Unit:

    def __init__(self, unit):
        self.img, self.frame_set = animation_loader.load_animation(unit)
        self.animation = 'walkup'
        self.frame = 0
        self.state = 'idle'
        self.x = 10
        self.y = 10

    def get_next_frame(self):
        if self.state == 'moving':
            self.frame = self.frame + 1
            if self.frame >= len(self.frame_set.get(self.animation)):
                self.frame = 0
        elif self.state == 'idle':
            self.frame = 0

        return pyglet.sprite.Sprite(self.frame_set.get(self.animation)[self.frame], self.x, self.y)

    def change_animation(self, animation):
        if self.animation != animation:
            self.animation = animation
            self.frame = 0

    def set_state(self, state):
        self.state = state

def update(dt):
    global dark_elf_draw
    dark_elf_draw = dark_elf.get_next_frame()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.W:
        dark_elf.change_animation('walkup')
        dark_elf.set_state('moving')
    elif symbol == key.S:
        dark_elf.change_animation('walkdown')
        dark_elf.set_state('moving')
    elif symbol == key.A:
        dark_elf.change_animation('walkleft')
        dark_elf.set_state('moving')
    elif symbol == key.D:
        dark_elf.change_animation('walkright')
        dark_elf.set_state('moving')

@window.event
def on_key_release(symbol, modifiers):
    if symbol == key.W:
        dark_elf.change_animation('walkup')
        dark_elf.set_state('idle')
    elif symbol == key.S:
        dark_elf.change_animation('walkdown')
        dark_elf.set_state('idle')
    elif symbol == key.A:
        dark_elf.change_animation('walkleft')
        dark_elf.set_state('idle')
    elif symbol == key.D:
        dark_elf.change_animation('walkright')
        dark_elf.set_state('idle')


@window.event
def on_draw():
    window.clear()
    dark_elf_draw.draw()

dark_elf = Unit('dark_elf')
dark_elf_draw = dark_elf.get_next_frame()
pyglet.clock.schedule_interval(update, 1 /30.0)
pyglet.app.run()
