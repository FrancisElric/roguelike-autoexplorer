import numpy as np
import tcod
import game.map_generation as map_gen
import game.tiles as tiles
from game.map_renderer import map_array_to_rgb


class Engine:
    def __init__(self, player, entities=()):
        self.player = player
        self.entities = entities
        self.level = 1
        # Map variables
        self.map_array = map_gen.pre_made(80, 60, "prefabs/map_1.txt")

        self.map_explored = np.zeros_like(self.map_array, dtype="bool")
        self.map_transparency = self.compute_transparency(self.map_array)
        self.update_rgb_with_fov()

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
            case tcod.event.KeyDown(sym=tcod.event.KeySym.MINUS):
                self.load_new_level()

    def render(self, context, console):
        console.clear()
        console.rgb[:] = self.map_rgb
        for entity in self.entities:
            console.print(
                entity.x,
                entity.y,
                text=entity.char,
                fg=entity.color,
            )

        console.print(
            self.player.x, self.player.y, text=self.player.char, fg=self.player.color
        )
        # player is separate to make sure it will be render last so it will be always visible
        context.present(console)

    def change_map(self, map_array):
        self.map_array = map_array
        self.map_transparency = self.compute_transparency(self.map_array)
        self.map_explored = np.zeros_like(self.map_array, dtype="bool")
        self.player.x, self.player.y = map_gen.spawn_point(self.map_array)
        self.update_rgb_with_fov()

    def try_moving(self, delta: tuple, entity):
        dx = entity.x - delta[0]
        dy = entity.y - delta[1]
        if self.map_array[dy, dx] != 1:
            entity.move(dx, dy)
            self.update_rgb_with_fov()

    def check_tile_interaction(self):
        print(self.map_array[self.player.y, self.player.x])
        if self.map_array[self.player.y, self.player.x] == tiles.TILE_STAIRS_DOWN:
            self.load_new_level()

    def load_new_level(self):
        match self.level:
            case 1:
                self.change_map(map_gen.random_walk(80, 60))
            case 2:
                self.change_map(map_gen.simplex_noise(80, 60))
            case _:
                self.change_map(map_gen.conway(80, 60))
        self.level += 1

    def compute_transparency(self, map_array):
        map_transparency = np.zeros_like(map_array, dtype="bool")
        with np.nditer(map_array, flags=["multi_index"]) as it:
            for x in it:
                map_transparency[it.multi_index] = not tiles.TILES_COLLISION[x]
        return map_transparency
        # return np.asarray(tiles.TILES_COLLISION)[map_array].astype("bool")

    def update_rgb_with_fov(self):
        self.map_visible = tcod.map.compute_fov(
            self.map_transparency,
            (self.player.y, self.player.x),
            radius=10,
            algorithm=tcod.constants.FOV_DIAMOND,
        )
        self.map_explored |= self.map_visible

        self.map_rgb = map_array_to_rgb(
            self.map_array, self.map_explored, self.map_visible
        )
