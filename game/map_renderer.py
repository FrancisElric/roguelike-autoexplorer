import numpy as np
import tcod
import time

from numpy.ma.core import empty

import game.tiles as tiles


def map_array_to_rgb(map_array, map_explored, map_visible):
    start_time = time.time()
    map_rgb = np.zeros_like(
        map_array,
        dtype=tcod.console.Console.DTYPE,
    )

    # Convert tiles.TILES_RGB to np array, so that np can do operations on it
    tile_rgb = np.array(tiles.TILES_RGB, dtype=tcod.console.Console.DTYPE)

    # This code works so much faster, but I barely get what is happening
    # In short [..., None] keeps old dimensions and adds a new one so that
    # map_rgb["bg"] can be compared to map_visible/map_explored
    # print(map_rgb["bg"].ndim) is 3
    # print(map_explored.ndim) is 2
    # print(map_visible.ndim) is 2
    # So we need that extra, empty dimensions to do vector operations

    map_rgb = tile_rgb[map_array]
    map_rgb = np.where(map_explored, map_rgb, tile_rgb[tiles.TILE_EMPTY])
    map_rgb["bg"] = np.where(map_explored[..., None], map_rgb["bg"], (0, 0, 0, 0))
    map_rgb["bg"] = np.where(~map_visible[..., None], map_rgb["bg"], (150, 150, 0, 255))

    print(f"rendering took {(time.time() - start_time) * 1000:2f} ms")
    return map_rgb
