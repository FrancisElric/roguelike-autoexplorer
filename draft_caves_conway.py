import numpy as np
import tcod


CYCLES = 3


def map_gen(width: int, height: int) -> np.ndarray:
    """
    Runs Conway’s Game of Life on a array of random ints for 4 cycles
    :param width:
    :param height:
    :return:
    """
    map_before = np.random.randint(low=0, high=2, size=(height, width))
    (
        map_before[0],
        map_before[-1],
        map_before[:, 0],
        map_before[:, -1],
    ) = (
        0,
        0,
        0,
        0,
    )
    map_buffer = np.zeros(
        shape=(height, width),
        dtype=tcod.console.Console.DTYPE,
    )

    for _ in range(CYCLES):
        map_after = np.zeros((height, width))
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                sum_of_all = (
                    np.sum(map_before[i - 1 : i + 2, j - 1 : j + 2]) - map_before[i, j]
                )
                # Rules of life
                # print(f'{"#"*20}')
                # print(f'visited {i},{j} and sum is {sum_of_all}')
                # print(f'selection: \n{map_before[i-1:i+2,j-1:j+2]}')
                if sum_of_all <= 1:
                    # print('sum_of_all <= 1')
                    map_after[i, j] = 0
                    continue
                if sum_of_all >= 4:
                    # print('sum_of_all >= 4')
                    map_after[i, j] = 0
                    continue
                if map_before[i, j] == 1 and sum_of_all in range(2, 4):
                    # print('map_before[i,j] == 1 and sum_of_all in range(2,4)')
                    map_after[i, j] = 1
                    continue
                if map_before[i, j] == 0 and sum_of_all == 3:
                    # print('map_before[i,j] == 0 and sum_of_all == 3')
                    map_after[i, j] = 1
                    continue
                # print('Out of cases')
                map_after[i, j] = 0
        map_before = map_after

    (
        map_before[0],
        map_before[-1],
        map_before[:, 0],
        map_before[:, -1],
    ) = (
        1,
        1,
        1,
        1,
    )
    with np.nditer(map_before, flags=["multi_index"]) as it:
        for x in it:
            if x[...] == 1:
                map_buffer["ch"][it.multi_index] = ord("#")
                map_buffer["fg"][it.multi_index] = (255, 255, 255, 255)
                map_buffer["bg"][it.multi_index] = (100, 100, 100, 255)
            else:
                map_buffer["ch"][it.multi_index] = ord(" ")
    return map_buffer
