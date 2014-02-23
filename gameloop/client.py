# encoding: utf-8
import network
import render
import server
import gamestate
s = server.Server()
s.startInThread()

import pyglet
from pyglet.window import key, mouse

import socket
from _socket import AF_INET, SOCK_STREAM
addr = ("localhost", 6666)
sock = socket.socket(AF_INET, SOCK_STREAM)
sock.connect(addr)
sock.setblocking(0)

window = pyglet.window.Window()

arrows = {"up": False, "down": False, "left": False, "right": False}
mouse.x = mouse.y = 0

class NetworkState:
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.createNewPacket(0, 0)

    def createNewPacket(self, last_mouse_x, last_mouse_y):
        self.packet = network.Packet()
        self.keyboard_state = network.KeyboardStateCommand({})
        self.mouse_state = network.MouseStateCommand(last_mouse_x, last_mouse_y)
        self.packet.addCommand(self.keyboard_state)
        self.packet.addCommand(self.mouse_state)

    def send(self):
        msg = self.packet.serialize()
        msg = "%04d%s" % (len(msg), msg)
        sock.send(msg)
        self.createNewPacket(self.mouse_state.x, self.mouse_state.y)

    def recv(self):
        msg = network.recv(sock)
        if msg is not None:
            packet = network.ServerPacket.deserialize(msg)
            for command in packet.commands:
                command.execute(self.gamestate)

camera = render.Camera(0, 0)
gamestate = gamestate.Gamestate(camera=camera)
netstate = NetworkState(gamestate)


@window.event
def on_draw():
    window.clear()
    gamestate.camera.draw(window.width, window.height)

@window.event
def on_mouse_press(x, y, button, modifiers):
    netstate.packet.addCommand(network.InputPressCommand(['MOUSE_DOWN']))

@window.event
def on_mouse_motion(x, y, dx, dy):
    netstate.mouse_state.x = x
    netstate.mouse_state.y = y

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
    netstate.keyboard_state.keys.update(arrows)

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
    netstate.keyboard_state.keys.update(arrows)

@window.event
def on_close():
    netstate.packet.addCommand(network.KillServerCommand())

def update(dt):
    netstate.recv()
    netstate.send()

pyglet.clock.schedule_interval(update, 1 / 30.0)
pyglet.app.run()