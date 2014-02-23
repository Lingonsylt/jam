# encoding: utf-8
class StubCamera:
    def addDrawable(self, obj):
        pass

class Gamestate(object):
    def __init__(self, inputstate = None, camera = None):
        self.camera = camera if camera else StubCamera()
        self.inputstate = inputstate

    def update(self, dt, packet):
        pass