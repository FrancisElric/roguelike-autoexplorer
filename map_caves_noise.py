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
    # map_array and map_buffer must use reversed dimensions (width <-> height)

    with np.nditer(map_array, op_flags=["readwrite"]) as it:
        for x in it:
            if x[...] < -0.2:
                x[...] = 1
            else:
                x[...] = 0

    return map_array
