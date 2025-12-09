import tcod
import random
import numpy as np
import time
import game.tiles as tiles
from game.entity import Entity


########## ENGINE CLASS ##########
class Engine:
    def __init__(self, player, context, console, entities=()):
        self.player = player
        self.entities = entities
        self.level = 1
        self.context = context
        self.console = console
        # # Map variables
        # self.map_explored = np.zeros_like(self.map_array, dtype="bool")
        # self.map_transparency = self.compute_transparency(self.map_array)
        # self.update_rgb_with_fov()

    def event_handling(self, event):
        match event:
            case tcod.event.Quit():
                raise SystemExit
            case tcod.event.KeyDown(sym=tcod.event.KeySym.LEFT):
                self.try_moving((1, 0), self.player)
            case tcod.event.KeyDown(sym=tcod.event.KeySym.RIGHT):
                self.try_moving((-1, 0), self.player)
            case tcod.event.KeyDown(sym=tcod.event.KeySym.UP):
                self.try_moving((0, 1), self.player)
            case tcod.event.KeyDown(sym=tcod.event.KeySym.DOWN):
                self.try_moving((0, -1), self.player)
            case tcod.event.KeyDown(sym=tcod.event.KeySym.RETURN):
                self.check_tile_interaction()
            case tcod.event.KeyDown(sym=tcod.event.KeySym.S):
                self.move_along_path(self.path_to_end)
            case tcod.event.KeyDown(sym=tcod.event.KeySym.A):
                self.autoexplore()
            case tcod.event.KeyDown(sym=tcod.event.KeySym.MINUS):
                self.load_new_level()
            case tcod.event.KeyDown(sym=tcod.event.KeySym.EQUALS):
                self.omnipresence()

    def render(self):
        self.console.clear()
        self.update_rgb_with_fov()
        self.console.rgb[:] = self.map_rgb
        for entity in self.entities:
            self.console.print(
                entity.x,
                entity.y,
                text=entity.char,
                fg=entity.color,
            )

        self.console.print(
            self.player.x, self.player.y, text=self.player.char, fg=self.player.color
        )
        # player is separate to make sure it will be render last so it will be always visible
        self.context.present(self.console)

    def change_map(self, map_type, preload=None):
        start_time = time.time()
        while True:
            match map_type:
                case "noise":
                    self.map_array = simplex_noise(80, 60)
                case "drunkards":
                    self.map_array = random_walk(80, 60)
                case "conway":
                    self.map_array = conway(80, 60)
                case "preload":
                    self.map_array = pre_made(80, 60, preload)
                # case "conw_and_drunkards":
                #     self.map_array = conw_and_drunkards()

            self.map_transparency = self.compute_transparency(self.map_array)
            start = look_for_element(self.map_array, tiles.TILE_STAIRS_UP)
            end = look_for_element(self.map_array, tiles.TILE_STAIRS_DOWN)

            graph = tcod.path.SimpleGraph(
                cost=self.map_transparency.astype("int8"),
                cardinal=1,
                diagonal=0,
            )
            pf = tcod.path.Pathfinder(graph)
            pf.add_root((start[1], start[0]))
            self.path_to_end = pf.path_to((end[1], end[0])).tolist()[1:]
            if self.path_to_end[1:] != []:
                break
        self.map_explored = np.zeros_like(self.map_array, dtype="bool")
        self.player.x, self.player.y = start[0], start[1]

    def try_moving(self, delta: tuple, entity):
        dx = entity.x - delta[0]
        dy = entity.y - delta[1]
        if self.map_array[dy, dx] != 1:
            entity.move(dx, dy)

    def check_tile_interaction(self):
        if self.map_array[self.player.y, self.player.x] == tiles.TILE_STAIRS_DOWN:
            self.load_new_level()

    def load_new_level(self):
        match self.level:
            case 1:
                self.change_map("drunkards")
            case 2:
                self.change_map("noise")
            case _:
                list_of_maps = ("drunkards", "noise", "conway")
                self.change_map(random.choice(list_of_maps))
        self.level += 1

    def compute_transparency(self, map_array):
        map_transparency = np.zeros_like(map_array, dtype="bool")
        with np.nditer(map_array, flags=["multi_index"]) as it:
            for x in it:
                map_transparency[it.multi_index] = not tiles.TILES_COLLISION[x]
        return map_transparency

    def update_rgb_with_fov(self):
        self.map_visible = tcod.map.compute_fov(
            self.map_transparency,
            (self.player.y, self.player.x),
            radius=15,
            algorithm=tcod.constants.FOV_DIAMOND,
        )
        self.map_explored |= self.map_visible

        self.map_rgb = map_array_to_rgb(
            self.map_array, self.map_explored, self.map_visible
        )

    def omnipresence(self):
        self.map_explored = np.ones_like(self.map_array, dtype="bool")

    def move_along_path(self, path):
        for y, x in path:
            dx = self.player.x - x
            dy = self.player.y - y
            self.try_moving((dx, dy), self.player)
            self.render()
            # time.sleep(0.03)

    def autoexplore(self):
        while True:
            path = self.new_dijkstra2d_map_and_path()
            if len(path) <= 1:
                break
            self.move_along_path(path)

    def new_dijkstra2d_map_and_path(self):
        cost = self.map_transparency
        dist = tcod.path.maxarray(shape=self.map_transparency.shape, dtype="int16")
        dist = np.where(self.map_explored == 0, 0, dist)
        tcod.path.dijkstra2d(dist, cost, cardinal=True, diagonal=None, out=dist)
        return tcod.path.hillclimb2d(dist, (self.player.y, self.player.x), True, False)


########## MAP RENDERING ##########
def map_array_to_rgb(map_array, map_explored, map_visible):
    start_time = time.time()
    map_rgb = np.zeros_like(
        map_array,
        dtype=tcod.console.Console.DTYPE,
    )

    # Convert tiles.TILES_RGB to np array, so that np can do operations on it
    tile_rgb = np.array(tiles.TILES_RGB, dtype=tcod.console.Console.DTYPE)

    # This code works so much faster, but I barely get what is happening
    # In short [..., None] keeps old dimensions and adds a new one so that
    # map_rgb["bg"] can be compared to map_visible/map_explored
    # print(map_rgb["bg"].ndim) is 3
    # print(map_explored.ndim) is 2
    # print(map_visible.ndim) is 2
    # So we need that extra, empty dimensions to do vector operations

    map_rgb = tile_rgb[map_array]
    map_rgb = np.where(map_explored, map_rgb, tile_rgb[tiles.TILE_EMPTY])
    map_rgb["bg"] = np.where(map_explored[..., None], map_rgb["bg"], (0, 0, 0, 0))
    map_rgb["bg"] = np.where(~map_visible[..., None], map_rgb["bg"], (150, 150, 0, 255))

    return map_rgb


########## MAP GENERATION ##########


def look_for_element(map_array, tile_element) -> tuple[int, int] | Exception:
    """Looks for an element in given map_array"""
    result = np.argwhere(map_array == tile_element)
    if result.size == 0:
        raise ValueError(f"Couldn't find {tile_element}")
    y, x = result[0]
    return int(x), int(y)


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
    DRUNKARDS = 30
    STRAIGHT_TIMER = 5  # fun to play with

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
    max_offset_width = int(width / 20)
    max_offset_height = int(height / 20)
    x = int(width / 2) + random.randint(-max_offset_width, max_offset_width)
    y = int(height / 2) + random.randint(-max_offset_height, max_offset_height)

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
    return map_array


def simplex_noise(width: int, height: int, seed: int = None):
    """
    Map generation based on simplex noise
    :param width:
    :param height:
    :param seed: for testing
    :return:
    """
    if seed == None:
        seed = random.randint(0, 255)
    start_time = time.time()
    map_noise = tcod.noise.Noise(
        dimensions=2,
        algorithm=tcod.noise.Algorithm.SIMPLEX,
        seed=seed,
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
    set_stairs(width, height, map_array)
    # TODO will need to fill up spaces that do not connect to center of the map
    return map_array


def pre_made(width: int = 80, height: int = 60, file_path: str = ""):
    # TODO for now I will trust _myself_ to pass map of a correct size, but in a future I'll need to handle this in code
    # TODO loadtxt vs genfromtxt? genfromtxt jest w stanie dodać brakujęce pola, więc wydaje się być bardziej future-proof?
    start_time = time.time()
    map_array = np.loadtxt(file_path, dtype="int8")
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


WIDTH, HEIGHT = 80, 60
# width ->>>>
# height -^^^^


def main() -> None:
    """Main loop"""

    # Load the font, 16 by 16, using DF layout
    # Font source: https://dwarffortresswiki.org/index.php/Tileset_repository#1.C3.971
    tileset = tcod.tileset.load_tilesheet(
        "assets/16x16-RogueYun-AgmEdit.png",
        16,
        16,
        tcod.tileset.CHARMAP_CP437,
    )

    # Create player
    player_x, player_y = 1, 1
    player = Entity(player_x, player_y, "☺", (255, 255, 0))

    # Create the main console.
    console = tcod.console.Console(WIDTH, HEIGHT)

    # Create a window based on this console and tileset.
    with tcod.context.new(
        columns=console.width,
        rows=console.height,
        tileset=tileset,
        title="Roguelike for CS50P",
        # New window for a console of size columns×rows.
    ) as context:
        engine = Engine(player, context, console)
        engine.change_map("preload", "prefabs/map_2.txt")
        while True:
            # Create engine instance
            engine.render()

            # This event loop will wait until at least one event is processed before exiting.
            # For a non-blocking event loop replace `tcod.event.wait` with `tcod.event.get`.
            for event in tcod.event.wait():
                # context.convert_event(event)  # Sets tile coordinates for mouse events.
                # DEBUG print(event)  # Print event names and attributes.
                engine.event_handling(event)


if __name__ == "__main__":
    main()
