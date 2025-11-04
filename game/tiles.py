tiles = (
    {"key": 0, "name": "floor", "collision": False},
    {"key": 1, "name": "wall", "collision": True},
)

# Tile types
TILE_EMPTY = 0
TILE_WALL = 1

# Tile collisions
TILES_COLLISION = [None] * 10
TILES_COLLISION[TILE_EMPTY] = False
TILES_COLLISION[TILE_WALL] = True
