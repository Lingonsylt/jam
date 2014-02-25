# encoding: utf-8
import network
import render
import server

import pyglet
from pyglet.window import key

class Client(pyglet.window.Window):
    def __init__(self, gamestate_cls, local_server=True):
        super(Client, self).__init__()
        self.set_size(gamestate_cls.width, gamestate_cls.height)
        self.direction_keys = {"up": False, "down": False, "left": False, "right": False}
        self.camera = render.Camera(0, 0)
        self.gamestate = gamestate_cls(camera=self.camera)
        self.netstate = network.ClientNetworkState(self.gamestate)

        if not self.netstate.connect():
            if local_server:
                s = server.Server(gamestate_cls)
                s.startInThread()
                if not self.netstate.connect():
                    raise Exception("Connection failed!")
            else:
                raise Exception("Connection failed!")

    def on_draw(self):
        self.clear()
        self.camera.draw(self.width, self.height)

    def on_mouse_press(self, x, y, button, modifiers):
        self.netstate.packet.addCommand(network.MouseClickCommand(button, x, y))

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.gamestate.camera.positionToAbsolute(x, y)
        self.netstate.mouse_state.x = x
        self.netstate.mouse_state.y = y

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.direction_keys["up"] = True
        elif symbol == key.S:
            self.direction_keys["down"] = True
        elif symbol == key.A:
            self.direction_keys["left"] = True
        elif symbol == key.D:
            self.direction_keys["right"] = True
        self.netstate.keyboard_state.keys.update(self.direction_keys)

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W:
            self.direction_keys["up"] = False
        elif symbol == key.S:
            self.direction_keys["down"] = False
        elif symbol == key.A:
            self.direction_keys["left"] = False
        elif symbol == key.D:
            self.direction_keys["right"] = False
        self.netstate.keyboard_state.keys.update(self.direction_keys)

    def on_close(self):
        self.netstate.packet.addCommand(network.KillServerCommand())

    def update(self, dt):
        self.netstate.recv()
        self.netstate.send()

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1 / 30.0)
        pyglet.app.run()