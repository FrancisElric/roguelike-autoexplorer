import numpy as np


def map_gen(width: int, height: int, file_path: str):
    # TODO for now I will trust _myself_ to pass map of a correct size, but in a future I'll need to handle this in code
    # TODO
    map_array = np.loadtxt(file_path, dtype="int8")
    return map_array
