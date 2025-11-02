import random
from pickle import GLOBAL

import numpy as np
import tcod

DURATION = 50
DRUNKARDS = 40
STRAIGHT_TIMER = 3


def map_gen(width: int, height: int) -> np.ndarray:
    """
    Map generation based on random walk
    :param width:
    :param height:
    :return:
    """
    map_array = np.ones((height, width))
    map_buffer = np.zeros(
        shape=(height, width),
        dtype=tcod.console.Console.DTYPE,
    )
    visited_cords = []

    def dig(x: int, y: int) -> tuple[int, int]:
        # Helper function that "digs" in map_array changing 1s to 0s
        if (x + dx) in range(1, height - 1):
            x += dx
        if (y + dy) in range(1, width - 1):
            y += dy
        map_array[x, y] = 0
        if (x, y) not in visited_cords:
            visited_cords.append((x, y))
        return x, y

    def random_direction() -> tuple[int, int]:
        # Helper function that chooses a random direction and returns delta
        x, y = (0, 0)
        match random.randint(1, 4):
            case 1:
                x += 1
            case 2:
                x -= 1
            case 3:
                y += 1
            case 4:
                y -= 1
        return x, y

    # A point to start the walk, set to center of the map_before
    x, y = int(width / 2), int(height / 2)

    for _ in range(DRUNKARDS):
        for _ in range(DURATION):
            dx, dy = random_direction()
            if random.randint(1, 15) == 1:
                for _ in range(STRAIGHT_TIMER):
                    x, y = dig(x, y)
            else:
                x, y = dig(x, y)
        x, y = random.choice(visited_cords)

    # This \/ will be later moved to a seperate file i think
    with np.nditer(map_array, flags=["multi_index"]) as it:
        for x in it:
            if x[...] == 1:
                map_buffer["ch"][it.multi_index] = ord("#")
                map_buffer["fg"][it.multi_index] = (255, 255, 255, 255)
                map_buffer["bg"][it.multi_index] = (100, 100, 100, 255)
            else:
                map_buffer["ch"][it.multi_index] = ord(" ")
    return map_buffer
