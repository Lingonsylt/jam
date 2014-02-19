# encoding: utf-8
NETWORK = False  # Nätverkssupport på/av
if NETWORK:
    import server
    server.startServerInThread()  # Dra igång en "server" som echo:ar tillbaka allt man skickar till den i en separat tråd

import pyglet
from pyglet.window import key, mouse
import math

if NETWORK:
    import socket
    from _socket import AF_INET, SOCK_STREAM
    import json
    addr = ("localhost", 6666)
    sock = socket.socket(AF_INET, SOCK_STREAM)
    sock.connect(addr)   # Koppla upp en socket mot servern
    sock.setblocking(0)  # Sätt socketen till non-blocking så att vi kan läsa från den utan att stanna upp hela programmet

window = pyglet.window.Window()  # Starta ett pyglet fönster (man kan ha flera)

hello_lazorkitten_label = pyglet.text.Label('Hello, lazorkitten!',  # Skapa ett text-objekt som kan ritas
                                            font_name='Times New Roman',
                                            font_size=36,
                                            x=window.width//2, y=window.height//2,
                                            anchor_x='center', anchor_y='center')

kitten_png = pyglet.resource.image('kitten.png')  # Ladda en katt-bild från fil
kitten_png.anchor_x = kitten_png.width / 2        # Sätt rotationspunkten för katten till mitt på
kitten_png.anchor_y = kitten_png.height / 2       #   (istället för övre vänstra hörnet)

kitten = pyglet.sprite.Sprite(kitten_png, window.width / 2, window.height / 2)  # Skapa en Sprite, en "instans" av kattbilden, med en bestämd position: mitt på skärmen
kitten.scale = 0.3  # Skala ner katten till 30%
kitten.speed = 500  # Sätt attributet speed till 500 (har inget att göra med pyglet)

lazor_png = pyglet.resource.image('lazor.png')  # Ladda en lazor-bild från fil
lazor_png.anchor_x = lazor_png.width / 2        # Sätt rotationspunkten för lazorn till mitt på
lazor_png.anchor_y = lazor_png.height / 2       #  (istället för övre vänstra hörnet)

lazors = []  # Håll reda på alla lazors som ska renderas

local_arrows = {"up": False, "down": False, "left": False, "right": False}  # Håll reda på vilka knappar som klienten trycker ner (skickas till servern och uppdaterar "arrows" om NETWORK == True)
arrows = {"up": False, "down": False, "left": False, "right": False}        # Håll reda på vilka knappar som servern har sagt är nedtryckta (om NETWORK == True)

mouse.x = mouse.y = 0  # Skapa x/y-attribut på mouse-modulen (Har inget med pyglet att göra)


@window.event       # Decorator som gör detta under the hood: window.on_draw = on_draw, alltså sätter en callback handler
def on_draw():      # Funktion som kallas varje gång pyglet är redo att rita. Vilket är... ofta?
    window.clear()  # Cleara hela fönstret (fyll med svart)
    kitten.draw()   # Rita spriten kitten (på position kitten.x/kitten.y

    for lazor in lazors:  # Rita alla lazor-sprites (borde göras i en "batch" för att rendera snabbare)
        lazor.draw()

    hello_lazorkitten_label.draw()  # Rita texten

    if NETWORK:
        networkUpdate()  # Läs uppdateringar från nätverket

def networkUpdate():
    try:
        msg = server.recv(sock)         # Läs ett meddelande från socketen (server.recv läser först en 4-digit meddelande-längd, sedan X bytes)
        arrows.update(json.loads(msg))  # Uppdatera de nedtryckta knapparna med den data vi fått från servern (dekoda med json)
    except socket.error, e:
        err = e.args[0]
        if err != socket.errno.EAGAIN and err != socket.errno.EWOULDBLOCK:  # Kasta exception om så länge felet inte är "ingen data just nu"
            raise

def get_lazor(x, y, rot):
    lazor = pyglet.sprite.Sprite(lazor_png, x, y)  # Skapa en Sprite, en "instans" av lazorbilden, på pos (x, y)
    lazor.speed = 600     # Sätt attributet speed till 500 (har inget att göra med pyglet)
    lazor.rotation = rot  # Sätt lazorns rotation till samma som kattens rotation
    lazor.scale = 0.6     # Skala lazorn till 60%
    return lazor

@window.event  # Decorator som gör detta under the hood: window.on_mouse_press = on_mouse_press, alltså sätter en callback handler
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        # Skapa en lazor-sprite i kattens vänstra öga och lägg till den i lazors-listan
        lazors.append(get_lazor(kitten.x + (kitten.height / 2) * 0.5 * math.sin(kitten.rotation * (math.pi / 180)) +
                                (kitten.width / 2) * 0.2 * math.sin((kitten.rotation - 90) * (math.pi / 180)),
                                kitten.y + (kitten.height / 2) * 0.5 * math.cos(kitten.rotation * (math.pi / 180)) +
                                (kitten.width / 2) * 0.2 * math.cos((kitten.rotation - 90) * (math.pi / 180)), kitten.rotation))

        # Skapa en lazor-sprite i kattens högra öga och lägg till den i lazors-listan
        lazors.append(get_lazor(kitten.x + (kitten.height / 2) * 0.5 * math.sin(kitten.rotation * (math.pi / 180)) -
                                (kitten.width / 2) * 0.2 * math.sin((kitten.rotation - 90) * (math.pi / 180)),
                                kitten.y + (kitten.height / 2) * 0.5 * math.cos(kitten.rotation * (math.pi / 180)) -
                                (kitten.width / 2) * 0.2 * math.cos((kitten.rotation - 90) * (math.pi / 180)), kitten.rotation))

@window.event # Decorator som gör detta under the hood: window.on_mouse_motion = on_mouse_motion, alltså sätter en callback handler
def on_mouse_motion(x, y, dx, dy):
    mouse.x = x  # Sätt mouse.x/y varje gång man rör musen
    mouse.y = y

def send(obj):                        # Skicka ett objekt till servern
    msg = json.dumps(obj)             # JSON-koda obj
    msg = "%04d%s" % (len(msg), msg)  # Sätt jsonmeddelandets längd som en 4-digit sträng följt av meddelandet
    sock.send(msg)

@window.event  # Decorator som gör detta under the hood: window.on_key_press = on_key_press, alltså sätter en callback handler
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
        send(local_arrows)  # Skicka de nedtryckta knapparna till servern
    else:
        arrows.update(local_arrows)  # Uppdatera arrows med innehållet i local_arrows

@window.event # Decorator som gör detta under the hood: window.on_key_release = on_key_release, alltså sätter en callback handler
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
        send(local_arrows)  # Skicka de nedtryckta knapparna till servern
    else:
        arrows.update(local_arrows)  # Uppdatera arrows med innehållet i local_arrows

@window.event  # Decorator som gör detta under the hood: window.on_close = on_close, alltså sätter en callback handler
def on_close():
    if NETWORK:
        send("DIE!")  # Säg åt servern att stänga av sig

def update(dt):  # Körs 120 gånger per skund, schemaläggs med pyglet.clock.schedule_interval() under denna funktion
    # Flytta katten kitten.speed gånger delta time i de riktningar som knapparna är nedtryckta
    if arrows["up"]:
        kitten.y += kitten.speed * dt
    if arrows["down"]:
        kitten.y -= kitten.speed * dt
    if arrows["left"]:
        kitten.x -= kitten.speed * dt
    if arrows["right"]:
        kitten.x += kitten.speed * dt

    kitten.rotation = math.atan2(mouse.x - kitten.x, mouse.y - kitten.y) * 180 / math.pi  # Rotera katten så att den pekar mot musen (lazorkitten will exterminate all mice on earth!)

    delete_lazors = []    # Håll reda på vilka lazors som hamnat utanför skärmen
    for lazor in lazors:  # Kör alla lazors framåt i lazor.speed gånger delta time
        lazor.x += math.sin(lazor.rotation * (math.pi / 180)) * lazor.speed * dt
        lazor.y += math.cos(lazor.rotation * (math.pi / 180)) * lazor.speed * dt

        if lazor.x < 0 or lazor.x > window.width or lazor.y < 0 or lazor.y > window.height:
            delete_lazors.append(lazor)  # Markera lazorn som borttagen om den är utanför skärmen

    for lazor in delete_lazors:  # Ta bort alla lazors som markerats som borttagna från listan "lazors"
        lazors.remove(lazor)

pyglet.clock.schedule_interval(update, 1/120.0)  # Schemalägg funktionen "update" att köras 120 gånger i sekunden
pyglet.app.run()                                 # Let the games begin!