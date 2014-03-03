# encoding: utf-8
import entity
import random
import render

class Tile(entity.Entity):
    image_path = "path_not_set"
    sprite_size = 32
    sprite_index = 0
    passable = True

    def __init__(self):
        self.animations = {
            'default': render.Animation(
                lambda: render.Spritesheet(self.image_path,
                                           self.sprite_size).getSprite(self.sprite_index, 0, 0, None))
        }
        super(Tile, self).__init__(0, 0, 0, anim_name='default')

    @classmethod
    def getVariations(cls):
        return [cls]

class VariationTile(Tile):
    sprite_start = 0
    sprite_length = 0
    sprite_index = None
    def __init__(self, sprite_index):
        self.animations = {
            'default': render.Animation(
                lambda: render.Spritesheet(self.image_path,
                                           self.sprite_size).getSprite(sprite_index, 0, 0, None))
        }
        super(Tile, self).__init__(0, 0, 0, anim_name='default')

    @classmethod
    def getVariations(cls):
        return [(lambda y: lambda: cls(y))(x) for x in range(cls.sprite_start, cls.sprite_start + cls.sprite_length)]

class Map:
    def __init__(self, width, height, tilesize=32):
        self.width = width
        self.height = height
        self.tilesize = tilesize
        self.tiles = [[None for _ in range(width)] for _ in range(height)]

    def setTile(self, idx_x, idx_y, tile):
        tile.x = idx_x * self.tilesize
        tile.y = idx_y * self.tilesize
        self.tiles[idx_y][idx_x] = tile

    def getIndexAt(self, x, y):
        return int(x // self.tilesize), int(y // self.tilesize)

    def getTile(self, idx_x, idx_y):
        return self.tiles[idx_y][idx_x]

    def getTileAt(self, x, y):
        return self.getTile(*self.getIndexAt(x, y))

    def draw(self):
        for row in self.tiles:
            for tile in row:
                tile.draw()

class MapGenerator:
    def __init__(self, passable_tiles, impassable_tiles):
        self.passable_tiles = passable_tiles
        self.impassable_tiles = impassable_tiles

    def generateLevel(self, m):
        return NotImplementedError("Start tile"), NotImplementedError("End tile")

class RandomMapGenerator(MapGenerator):
    def generateLevel(self, m):
        for rownum in range(m.height):
            for colnum in range(m.width):
                m.setTile(colnum, rownum, random.sample(self.passable_tiles, 1)[0]())
        return m.getTile(random.randint(0, m.width - 1), random.randint(0, m.height - 1)), \
            m.getTile(random.randint(0, m.width - 1), random.randint(0, m.height - 1))

if __name__ == "__main__":
    m = Map(width=10, height=10, tilesize=32)
    assert m.getIndexAt(10, 15) == (0, 0)
    assert m.getIndexAt(32, 32) == (1, 1)
    tile = Tile()
    m.setTile(2, 2, tile)
    assert (tile.x, tile.y) == (64, 64)
    assert m.getTileAt(70, 70) == tile

    class ImpassableGrassTile(Tile):
        image_path = "res/gras_tiles.png"
        sprite_index = 1
        passable = False

    class LightGrassTile(VariationTile):
        image_path = "res/gras_tiles.png"
        sprite_start = 0
        sprite_length = 4

    class DarkGrassTile(VariationTile):
        image_path = "res/gras_tiles.png"
        sprite_start = 4
        sprite_length = 5

    g = RandomMapGenerator(LightGrassTile.getVariations() + DarkGrassTile.getVariations(),
                           ImpassableGrassTile.getVariations())
    start_tile, end_tile = g.generateLevel(m)

    def _render():
        m.draw()
    render.render(_render)