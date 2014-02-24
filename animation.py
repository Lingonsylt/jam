import pyglet
from pyglet.window import key
import animation_loader

window = pyglet.window.Window()

class Unit:

    def __init__(self, unit):
        self.img, self.frame_set = animation_loader.load_animation(unit)
        self.animation = 'walkup'
        self.frame = 0
        self.x = 10
        self.y = 10

    def get_next_frame(self):
        self.frame = self.frame + 1
        if self.frame >= len(self.frame_set.get(self.animation)):
            self.frame = 0

        return pyglet.sprite.Sprite(self.frame_set.get(self.animation)[self.frame], self.x, self.y)
    
    def change_animation(self, animation):
        if self.animation != animation:
            self.animation = animation
            self.frame = 0

def update(dt):
    global dark_elf_draw
    dark_elf_draw = dark_elf.get_next_frame()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.W:
        dark_elf.change_animation('walkup')
    elif symbol == key.S:
        dark_elf.change_animation('walkdown')
    elif symbol == key.A:
        dark_elf.change_animation('walkleft')
    elif symbol == key.D:
        dark_elf.change_animation('walkright')

@window.event
def on_draw():
    global dark_elf
    window.clear()
    dark_elf_draw.draw()

dark_elf = Unit('dark_elf')
dark_elf_draw = dark_elf.get_next_frame()
pyglet.clock.schedule_interval(update, 1 /30.0)
pyglet.app.run()
