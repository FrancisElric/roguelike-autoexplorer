import numpy as np
import tcod


def render_map(map_array):
    map_buffer = np.zeros_like(
        map_array,
        dtype=tcod.console.Console.DTYPE,
    )

    with np.nditer(map_array, flags=["multi_index"]) as it:
        for x in it:
            if x[...] == 1:
                map_buffer["ch"][it.multi_index] = ord("#")
                map_buffer["fg"][it.multi_index] = (255, 255, 255, 255)
                map_buffer["bg"][it.multi_index] = (100, 100, 100, 255)
            else:
                map_buffer["ch"][it.multi_index] = ord(" ")
    return map_buffer


def map_array_inverter(map_array):
    with np.nditer(map_array, op_flags=["readwrite"]) as it:
        for x in it:
            if x[...] == 1:
                x[...] = 0
            elif x[...] == 0:
                x[...] = 1
    return map_array
