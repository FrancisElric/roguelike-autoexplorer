import random
import numpy as np
import tcod
import time
import game.map_generation as map_gen
import game.tiles as tiles
from game.map_renderer import map_array_to_rgb


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
                    self.map_array = map_gen.simplex_noise(80, 60)
                case "drunkards":
                    self.map_array = map_gen.random_walk(80, 60)
                case "conway":
                    self.map_array = map_gen.conway(80, 60)
                case "preload":
                    self.map_array = map_gen.pre_made(80, 60, preload)
                case "conw_and_drunkards":
                    self.map_array = map_gen.conw_and_drunkards()

            self.map_transparency = self.compute_transparency(self.map_array)
            start = map_gen.look_for_element(self.map_array, tiles.TILE_STAIRS_UP)
            end = map_gen.look_for_element(self.map_array, tiles.TILE_STAIRS_DOWN)

            graph = tcod.path.SimpleGraph(
                cost=self.map_transparency.astype("int8"),
                cardinal=1,
                diagonal=0,
            )
            pf = tcod.path.Pathfinder(graph)
            pf.add_root((start[1], start[0]))
            self.path_to_end = pf.path_to((end[1], end[0])).tolist()[1:]
            print(self.path_to_end)
            if self.path_to_end[1:] != []:
                break
            print("Map skipped, no path")
        self.map_explored = np.zeros_like(self.map_array, dtype="bool")
        self.player.x, self.player.y = start[0], start[1]
        print(f"map changing took {(time.time() - start_time) * 1000:2f} ms")

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
                print("DONE")
                break
            self.move_along_path(path)

    def new_dijkstra2d_map_and_path(self):
        cost = self.map_transparency
        dist = tcod.path.maxarray(shape=self.map_transparency.shape, dtype="int16")
        dist = np.where(self.map_explored == 0, 0, dist)
        tcod.path.dijkstra2d(dist, cost, cardinal=True, diagonal=None, out=dist)
        return tcod.path.hillclimb2d(dist, (self.player.y, self.player.x), True, False)
