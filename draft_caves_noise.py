import numpy as np
import random
import tcod


def map_gen(width: int, height: int) -> np.array:
    """
    Map generation based on simplex noise
    :param width:
    :param height:
    :return:
    """
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
    # TODO add this when I move map_buffer rendering to a different step

    map_buffer = np.zeros(
        shape=(height, width),
        dtype=tcod.console.Console.DTYPE,
    )
    # map_array and map_buffer must use reversed dimensions (width <-> height)

    # This \/ will be later moved to a seperate file i think
    with np.nditer(map_array, flags=["multi_index"]) as it:
        for x in it:
            if x[...] < -0.2:
                map_buffer["ch"][it.multi_index] = ord("#")
                map_buffer["fg"][it.multi_index] = (255, 255, 255, 255)
                map_buffer["bg"][it.multi_index] = (100, 100, 100, 255)
            else:
                map_buffer["ch"][it.multi_index] = ord(" ")

    return map_buffer
