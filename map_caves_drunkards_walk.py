import random
import numpy as np

DURATION = 50
DRUNKARDS = 40
STRAIGHT_TIMER = 3


def map_gen(width: int, height: int, map_array=None) -> np.ndarray:
    """
    Map generation based on random walk
    :param width:
    :param height:
    :param map_array (optional)
    :return:
    """
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

    return map_array
