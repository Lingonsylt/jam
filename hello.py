# encoding: utf-8
# Nätverkssupport på/av
NETWORK = False

if NETWORK:
    # Dra igång en "server" som echo:ar tillbaka allt man skickar till den i en separat tråd
    import server
    server.startServerInThread()

import pyglet
from pyglet.window import key
from pyglet.window import mouse
import math

if NETWORK:
    # Koppla upp en socket mot servern
    import socket
    from _socket import AF_INET, SOCK_STREAM
    import json
    addr = ("localhost", 6666)
    sock = socket.socket(AF_INET, SOCK_STREAM)
    sock.connect(addr)

    # Sätt socketen till non-blocking så att vi kan läsa från den utan att stanna upp hela programmet
    sock.setblocking(0)

# Starta ett pyglet fönster (man kan ha flera)
window = pyglet.window.Window()

# Skapa ett text-objekt
hello_lazorkitten_label = pyglet.text.Label('Hello, lazorkitten!',
                                            font_name='Times New Roman',
                                            font_size=36,
                                            x=window.width//2, y=window.height//2,
                                            anchor_x='center', anchor_y='center')

# Ladda en katt-bild från fil
kitten_png = pyglet.resource.image('kitten.png')

# Sätt rotationspunkten för katten till mitt på (istället för övre vänstra hörnet)
kitten_png.anchor_x = kitten_png.width / 2
kitten_png.anchor_y = kitten_png.height / 2

# Skapa en Sprite, en "instans" av kattbilden, med en bestämd position: mitt på skärmen
kitten = pyglet.sprite.Sprite(kitten_png, window.width / 2, window.height / 2)

# Skala ner katten till 30%
kitten.scale = 0.3

# Sätt attributet speed till 500 (har inget att göra med pyglet)
kitten.speed = 500

# Ladda en lazor-bild från fil
lazor_png = pyglet.resource.image('lazor.png')

# Sätt rotationspunkten för lazorn till mitt på (istället för övre vänstra hörnet)
lazor_png.anchor_x = lazor_png.width / 2
lazor_png.anchor_y = lazor_png.height / 2

# Håll reda på alla lazors som ska renderas
lazors = []

# Håll reda på vilka knappar som är nedtryckta
arrows = {"up": False, "down": False, "left": False, "right": False}

# Håll reda på vilka knappar som klienten trycker ner (skickas till servern och uppdaterar "arrows" om NETWORK == True)
local_arrows = {"up": False, "down": False, "left": False, "right": False}

# Skapa x/y-attribut på mouse-modulen (Har inget med pyglet att göra)
mouse.x = 0
mouse.y = 0


# Funktion som kallas varje gång pyglet är redo att rita. Vilket är... ofta?
@window.event
def on_draw():
    # Cleara hela fönstret (fyll med svart)
    window.clear()

    # Rita spriten kitten (på position kitten.x/kitten.y
    kitten.draw()

    # Rita alla lazor-sprites (borde göras i en "batch" för att rendera snabbare)
    for lazor in lazors:
        lazor.draw()

    # Rita texten
    hello_lazorkitten_label.draw()

    if NETWORK:
        # Läs uppdateringar från nätverket
        networkUpdate()


def networkUpdate():
    try:
        # Läs ett meddelande från socketen (server.recv läser först en 4-digit meddelande-längd, sedan X bytes)
        msg = server.recv(sock)

        # Uppdatera de nedtryckta knapparna med den data vi fått från servern (dekoda med json)
        arrows.update(json.loads(msg))
    except socket.error, e:
        err = e.args[0]
        # Kasta exception om så länge felet inte är "ingen data just nu"
        if err != socket.errno.EAGAIN and err != socket.errno.EWOULDBLOCK:
            raise


def get_lazor(x, y, rot):
    # Skapa en Sprite, en "instans" av kattbilden, på pos (x, y)
    lazor = pyglet.sprite.Sprite(lazor_png, x, y)

    # Sätt attributet speed till 500 (har inget att göra med pyglet)
    lazor.speed = 600

    # Sätt lazorns rotation till samma som kattens
    lazor.rotation = rot

    # Skala lazorn till 60%
    lazor.scale = 0.6
    return lazor

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        # Skapa en lazor i kattens vänstra öga och lägg till den i lazors-listan
        lazors.append(get_lazor(kitten.x + (kitten.height / 2) * 0.5 * math.sin(kitten.rotation * (math.pi / 180)) +
                                (kitten.width / 2) * 0.2 * math.sin((kitten.rotation - 90) * (math.pi / 180)),
                                kitten.y + (kitten.height / 2) * 0.5 * math.cos(kitten.rotation * (math.pi / 180)) +
                                (kitten.width / 2) * 0.2 * math.cos((kitten.rotation - 90) * (math.pi / 180)), kitten.rotation))

        # Skapa en lazor i kattens högra öga och lägg till den i lazors-listan
        lazors.append(get_lazor(kitten.x + (kitten.height / 2) * 0.5 * math.sin(kitten.rotation * (math.pi / 180)) -
                                (kitten.width / 2) * 0.2 * math.sin((kitten.rotation - 90) * (math.pi / 180)),
                                kitten.y + (kitten.height / 2) * 0.5 * math.cos(kitten.rotation * (math.pi / 180)) -
                                (kitten.width / 2) * 0.2 * math.cos((kitten.rotation - 90) * (math.pi / 180)), kitten.rotation))


@window.event
def on_mouse_motion(x, y, dx, dy):
    # Sätt mouse.x/y varje gång man rör musen
    mouse.x = x
    mouse.y = y

def send(obj):
    # JSON-koda obj och skicka jsonmeddelandets längd som en 4-digit sträng följt av meddelandet
    msg = json.dumps(obj)
    msg = "%04d%s" % (len(msg), msg)
    sock.send(msg)

@window.event
def on_key_press(symbol, modifiers):
    # Registrera nedtryckning av knappar
    if symbol == key.W:
        local_arrows["up"] = True
    elif symbol == key.S:
        local_arrows["down"] = True
    elif symbol == key.A:
        local_arrows["left"] = True
    elif symbol == key.D:
        local_arrows["right"] = True
    if NETWORK:
        # Skicka de nedtryckta knapparna till servern
        send(local_arrows)
    else:
        # Uppdatera arrows med innehållet i local_arrows
        arrows.update(local_arrows)

@window.event
def on_key_release(symbol, modifiers):
    # Registrera släppning av knappar
    if symbol == key.W:
        local_arrows["up"] = False
    elif symbol == key.S:
        local_arrows["down"] = False
    elif symbol == key.A:
        local_arrows["left"] = False
    elif symbol == key.D:
        local_arrows["right"] = False
    if NETWORK:
        # Skicka de nedtryckta knapparna till servern
        send(local_arrows)
    else:
        # Uppdatera arrows med innehållet i local_arrows
        arrows.update(local_arrows)


def update(dt):
    # Flytta katten kitten.speed gånger delta time i de riktningar som knapparna är nedtryckta
    if arrows["up"]:
        kitten.y += kitten.speed * dt
    if arrows["down"]:
        kitten.y -= kitten.speed * dt
    if arrows["left"]:
        kitten.x -= kitten.speed * dt
    if arrows["right"]:
        kitten.x += kitten.speed * dt

    # Rotera katten så att den pekar mot musen (lazorkitten will exterminate all mice on earth!)
    kitten.rotation = math.atan2(mouse.x - kitten.x, mouse.y - kitten.y) * 180 / math.pi

    # Håll reda på vilka lazors som hamnat utanför skärmen
    delete_lazors = []

    # Kör alla lazors framåt
    for lazor in lazors:
        lazor.x += math.sin(lazor.rotation * (math.pi / 180)) * lazor.speed * dt
        lazor.y += math.cos(lazor.rotation * (math.pi / 180)) * lazor.speed * dt

        # Markera lazorn som borttagen om den är utanför skärmen
        if lazor.x < 0 or lazor.x > window.width or lazor.y < 0 or lazor.y > window.height:
            delete_lazors.append(lazor)

    # Ta bort alla lazors som markerats som borttagna från listan "lazors"
    for lazor in delete_lazors:
        lazors.remove(lazor)

@window.event
def on_close():
    if NETWORK:
        # Säg åt servern att stänga av sig
        send("DIE!")


# Schemalägg funktionen "update" att köras 120 gånger i sekunden
pyglet.clock.schedule_interval(update, 1/120.0)

# Let the games begin!
pyglet.app.run()