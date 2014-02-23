import entities
import network


class StubCamera:
    def addDrawable(self, obj):
        pass

class Gamestate:
    def __init__(self, inputstate = None, camera = None):
        self.camera = camera if camera else StubCamera()
        self.inputstate = inputstate

        player = entities.Player(0, 0, 0, 0)
        self.camera.addDrawable(player)
        self.players = {
            player.id: player
        }

    def update(self, dt, packet):
        for player in self.players.values():
            player.update(dt, self.inputstate)

        for player in self.players.values():
            packet.addCommand(network.PlayerStateCommand(player))