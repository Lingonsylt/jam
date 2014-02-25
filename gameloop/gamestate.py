# encoding: utf-8
import network

class StubCamera:
    def addDrawable(self, obj):
        pass

class Gamestate(object):
    width = 640
    height = 480

    def __init__(self, clients=None, inputstate=None, camera=None):
        self._networked_entities = {}
        self._networked_entity_id_next = 0
        self.camera = camera if camera else StubCamera()
        self.clients = clients
        self.inputstate = inputstate

    def _updateNetworkedEntities(self, dt, packet):
        for entity in self._networked_entities.values():
            entity.update(dt, self, self.clients[entity.client_id].inputstate, packet)
            packet.addCommand(network.UpdateNetworkedEntityCommand(entity))

    def onNewClient(self, client, packet, client_packet):
        pass

    def _onNewClient(self, client, packet, client_packet):
        for entity in self._networked_entities.values():
            client_packet.addCommand(network.CreateNetworkedEntityCommand(entity))

    def update(self, dt, packet):
        pass