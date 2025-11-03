import numpy as np
import tcod


CYCLES = 2


def map_gen(width: int, height: int, map_array=None) -> np.ndarray:
    """
    Runs Conway’s Game of Life on a array of random ints for 4 cycles
    :param width:
    :param height:
    :param map_array:
    :return:
    """
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
        map_after = np.zeros((height, width))
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                sum_of_all = (
                    np.sum(map_array[i - 1 : i + 2, j - 1 : j + 2]) - map_array[i, j]
                )
                # TODO change rules to produce better caves
                # Rules of life
                # print(f'{"#"*20}')
                # print(f'visited {i},{j} and sum is {sum_of_all}')
                # print(f'selection: \n{map_array[i-1:i+2,j-1:j+2]}')
                if sum_of_all <= 1:
                    # print('sum_of_all <= 1')
                    map_after[i, j] = 0
                    continue
                if sum_of_all >= 4:
                    # print('sum_of_all >= 4')
                    map_after[i, j] = 0
                    continue
                if map_array[i, j] == 1 and sum_of_all in range(2, 4):
                    # print('map_array[i,j] == 1 and sum_of_all in range(2,4)')
                    map_after[i, j] = 1
                    continue
                if map_array[i, j] == 0 and sum_of_all == 3:
                    # print('map_array[i,j] == 0 and sum_of_all == 3')
                    map_after[i, j] = 1
                    continue
                # print('Out of cases')
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
    return map_array
