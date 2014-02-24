Kitten in the Dark
=============

TODO
====

Tiled map
===

```python
m = Map(width=10, height=10, tilesize=32)
tile = Tile(x=0, y=0, passable=True, createSpriteCallback=lambda: pyglet.sprite.Sprite(img))
m.getIndexAt(10,15) == (0, 0)
m.setTile(**m.getIndexAt(tile.x, tile.y), tile)
m.getTileAt(10, 15) == tile
```

Dungeon generator
===
```python
g = DungeonGenerator(hall_size=10)
m = Map(width=10, height=10, tilesize=32)
start_tile, goal_tile = g.generateLevel(m)
```

Map collision detection
===
```python
m = Map(width=10, height=10, tilesize=32)
m.isPassable(x=15, y=10)
```

Ray collision detection
===
```python
g = Gamestate(...)
g.rayCollides(src_x=0, src_y=0, dst_x=50, dst_y=50) == [entity1, entity2, ...]
```

Box/circle collision detection
===
```python
g = Gamestate(...)
g.circleCollides(x=10, y=10, radius=50) == [entity1, entity2, ...]
g.boxCollides(x=10, y=10, width=50, height=50) == [entity1, entity2, ...]
```

Pathfinding
===
```python
m = Map(width=10, height=10, tilesize=32)
p = Pathfinder(map=m, obstacles=[entity1, ...])
p.walkTowards(src_x=0, src_y=0, dst_x=50, dst_y=0, speed=10) == (10, 0)
p.distanceTo(src_x=0, src_y=0, dst_x=50, dst_y=0) == 50
```

AI
===
```python
m = Monster(...)
m.update(dt, ...)  # Kill all the players!
```

Sprite sheet
===
```python
from gameloop.render import Spritesheet
s = Spritesheet("image.png", sprite_size=32)
s.getSprite(0, x=10, y=10)
```

Sprite animation
===
```python
s = Spritesheet("image.png")
a = Animation(s, start=0, end=3, name="idle")
a.getNextFrame()
a.draw()
```

Entity
===
```python
from gameloop.entity import Entity
e = Entity(x=10, y=10, rot=90, anim_name="idle")
a = Animation(s, start=0, end=3, name="walk")
e.animations[a.name] = a
e.update(dt, ...)
e.setAnimation("walk")
e.draw()
e.destroy()
```

Camera
===
```python
from gameloop.render import Camera
c = Camera(x=0, y=0)
a = Animation(...)
c.addDrawable(a)
c.draw()
c.removeDrawable(a)
```

Light effects
===
```python
m = Map(width=10, height=10, tilesize=32)
c = Camera(x=0, y=0)
c.drawLighting(m)  # Cool light effects that cast shadows from the walls
```

