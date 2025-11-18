from operator import truediv

import numpy as np
import tcod
import time
import random
import game.tiles as tiles


def look_for_element(map_array, tile_element) -> tuple[int, int] | Exception:
    """Looks for an element in given map_array"""
    result = np.argwhere(map_array == tile_element)
    if result.size == 0:
        raise ValueError(f"Couldn't find {tile_element}")
    y, x = result[0]
    return x, y


def set_stairs(width: int, height: int, map_array):
    """Adds stairs to given map_array"""
    x, y = 1, 1
    while tiles.TILES_COLLISION[map_array[y, x]]:
        x += 1
        y += 1
    map_array[y, x] = tiles.TILE_STAIRS_UP

    x, y = width - 2, height - 2
    while tiles.TILES_COLLISION[map_array[y, x]]:
        x -= 1
        y -= 1
    map_array[y, x] = tiles.TILE_STAIRS_DOWN

    return map_array


def conway(width: int, height: int, map_array=None) -> np.ndarray:
    """
    Runs Conway’s Game of Life on a array of random ints for 4 cycles
    :param width:
    :param height:
    :param map_array:
    :return:
    """
    CYCLES = 3
    start_time = time.time()
    if map_array is None:
        map_array = np.random.randint(low=0, high=2, size=(height, width))
        (
            map_array[0],
            map_array[-1],
            map_array[:, 0],
            map_array[:, -1],
        ) = (
            0,
            0,
            0,
            0,
        )
    for _ in range(CYCLES):
        map_after = np.zeros((height, width), dtype="int8")
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                sum_of_all = (
                    np.sum(map_array[i - 1 : i + 2, j - 1 : j + 2]) - map_array[i, j]
                )
                # TODO change rules to produce better caves
                # Rules of life
                if sum_of_all <= 1:
                    map_after[i, j] = 0
                    continue
                if sum_of_all >= 4:
                    map_after[i, j] = 0
                    continue
                if map_array[i, j] == 1 and sum_of_all in range(2, 4):
                    map_after[i, j] = 1
                    continue
                if map_array[i, j] == 0 and sum_of_all == 3:
                    map_after[i, j] = 1
                    continue
                map_after[i, j] = 0
        map_array = map_after

    (
        map_array[0],
        map_array[-1],
        map_array[:, 0],
        map_array[:, -1],
    ) = (
        1,
        1,
        1,
        1,
    )
    print(f"conway took {(time.time() - start_time) * 1000:2f} ms")
    set_stairs(width, height, map_array)
    return map_array


def random_walk(width: int, height: int, map_array=None) -> np.ndarray:
    """
    Map generation based on random walk
    :param width:
    :param height:
    :param map_array (optional)
    :return:
    """
    DURATION = 50
    DRUNKARDS = 50
    STRAIGHT_TIMER = 20  # fun to play with

    start_time = time.time()
    if map_array is None:
        map_array = np.ones((height, width), dtype="int8")
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
        return random.choice(((0, 1), (1, 0), (0, -1), (-1, 0)))

    # A point to start the walk, set to center of the map_before
    x, y = int(width / 2) + random.randint(-10, 10), int(height / 2) + random.randint(
        -10, 10
    )

    for _ in range(DRUNKARDS):
        for _ in range(DURATION):
            dx, dy = random_direction()
            if random.randint(1, 15) == 1:
                for _ in range(STRAIGHT_TIMER):
                    x, y = dig(x, y)
            else:
                x, y = dig(x, y)
        x, y = random.choice(visited_cords)

    # Custom stair setting function cuz main one would not work here
    visited_cords = sorted(visited_cords, key=lambda coord: (coord[1] + coord[0]))
    map_array[visited_cords[-1]] = tiles.TILE_STAIRS_DOWN
    map_array[visited_cords[0]] = tiles.TILE_STAIRS_UP
    print(f"drunkards took {(time.time() - start_time) * 1000:2f} ms")
    return map_array


def simplex_noise(width: int, height: int) -> np.array:
    """
    Map generation based on simplex noise
    :param width:
    :param height:
    :return:
    """
    start_time = time.time()
    map_noise = tcod.noise.Noise(
        dimensions=2,
        algorithm=tcod.noise.Algorithm.SIMPLEX,
        seed=random.randint(0, 255),
    )
    map_array = map_noise[tcod.noise.grid(shape=(width, height), scale=0.25)]
    (
        map_array[0],
        map_array[-1],
        map_array[:, 0],
        map_array[:, -1],
    ) = (
        -1,
        -1,
        -1,
        -1,
    )
    # map_array and map_rgb must use reversed dimensions (width <-> height)

    with np.nditer(map_array, op_flags=["readwrite"]) as it:
        for x in it:
            if x < -0.2:
                x[...] = 1
            else:
                x[...] = 0
    map_array = map_array.astype("int8")
    print(f"noise took {(time.time() - start_time) * 1000:2f} ms")
    set_stairs(width, height, map_array)
    # TODO will need to fill up spaces that do not connect to center of the map
    return map_array


def pre_made(width: int, height: int, file_path: str):
    # TODO for now I will trust _myself_ to pass map of a correct size, but in a future I'll need to handle this in code
    # TODO loadtxt vs genfromtxt? genfromtxt jest w stanie dodać brakujęce pola, więc wydaje się być bardziej future-proof?
    start_time = time.time()
    map_array = np.loadtxt(file_path, dtype="int8")
    print(f"premade took {(time.time() - start_time) * 1000:2f} ms")
    return map_array


def bool_map_array_adder(
    *maps,
    width: int = 80,
    height: int = 60,
    default_value: bool = False,
    operation: str = "or",
):
    map_array = np.zeros((height, width), dtype="bool")
    for map in maps:
        match default_value:
            case "or":
                map_array = np.logical_or(map_array, map)
            case "and":
                map_array = np.logical_and(map_array, map)

    map_array = map_array.astype("int8")
    set_stairs(width, height, map_array)
    return map_array
