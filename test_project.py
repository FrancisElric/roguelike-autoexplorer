import random
from itertools import dropwhile

import pytest
import numpy as np
from project import (
    look_for_element,
    set_stairs,
    conway,
    simplex_noise,
    random_walk,
    pre_made,
    map_array_to_rgb,
)

import game.tiles as tiles


@pytest.fixture(autouse=True)
def set_seed():
    random.seed(42)
    np.random.seed(42)


def test_pre_made():
    map_reference = np.array(
        [
            [1, 1, 1, 1, 1, 1],
            [1, 0, 2, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 3, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    map_test = pre_made(file_path="prefabs/test_map_1.txt")
    assert np.array_equal(map_reference, map_test)


def test_look_for_element():
    map_array_with_no_stairs = np.array(
        [
            [1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    with pytest.raises(ValueError):
        look_for_element(map_array_with_no_stairs, tiles.TILE_STAIRS_UP)
    map_array_with_stairs = np.array(
        [
            [1, 1, 1, 1, 1, 1],
            [1, 0, 2, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 3, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    assert look_for_element(map_array_with_stairs, tiles.TILE_STAIRS_UP) == (2, 1)
    assert look_for_element(map_array_with_stairs, tiles.TILE_STAIRS_DOWN) == (3, 3)


def test_set_stairs():
    # default case
    map_array = np.array(
        [
            [1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    map_array_result = np.array(
        [
            [1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 3, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    assert np.array_equal(map_array_result, set_stairs(6, 6, map_array))

    # case with obstacles
    map_array = np.array(
        [
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 1, 1],
            [1, 0, 0, 0, 1, 1],
            [1, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    map_array_result = np.array(
        [
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1],
            [1, 0, 2, 0, 1, 1],
            [1, 0, 0, 3, 1, 1],
            [1, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    assert np.array_equal(map_array_result, set_stairs(6, 6, map_array))


def test_simplex_noise():
    map_array_expected = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 0, 0, 1, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    assert np.array_equal(map_array_expected, simplex_noise(10, 10, 1))


def test_conway():
    map_array_expected = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    assert np.array_equal(map_array_expected, conway(10, 10))


def test_random_walk():
    map_array_expected = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        dtype="int8",
    )
    assert np.array_equal(map_array_expected, random_walk(10, 10))
