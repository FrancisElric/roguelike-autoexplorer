import numpy as np
import tcod
import time
import game.tiles as tiles


def map_array_to_rgb(map_array, map_explored, map_visible):
    start_time = time.time()
    map_rgb = np.zeros_like(
        map_array,
        dtype=tcod.console.Console.DTYPE,
    )

    with np.nditer(map_array, flags=["multi_index"]) as it:
        for x in it:
            if map_visible[it.multi_index]:
                map_rgb["ch"][it.multi_index] = tiles.TILES_RGB[x][0]
                map_rgb["fg"][it.multi_index] = tiles.TILES_RGB[x][1]
                map_rgb["bg"][it.multi_index] = (150, 150, 0, 255)
            elif map_explored[it.multi_index]:
                map_rgb["ch"][it.multi_index] = tiles.TILES_RGB[x][0]
                map_rgb["fg"][it.multi_index] = tiles.TILES_RGB[x][1]
                map_rgb["bg"][it.multi_index] = tiles.TILES_RGB[x][2]
            # if
    print(f"rendering took {(time.time() - start_time) * 1000:2f} ms")
    return map_rgb


def map_array_inverter(map_array):
    with np.nditer(map_array, op_flags=["readwrite"]) as it:
        for x in it:
            if x[...] == 1:
                x[...] = 0
            elif x[...] == 0:
                x[...] = 1

    return map_array
