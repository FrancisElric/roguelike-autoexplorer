import tcod
import game.map_generation as map_gen
import game.tiles as tiles
from game.map_renderer import render_map


class Engine:
    def __init__(self, map_array, map_buffer, player, entities=()):
        self.map_array = map_array
        self.map_buffer = map_buffer
        self.player = player
        self.entities = entities
        self.level = 1

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
        console.rgb[:] = self.map_buffer
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
        self.map_buffer = render_map(map_array)
        self.player.x, self.player.y = map_gen.spawn_point(self.map_array)

    def try_moving(self, delta: tuple, entity):
        dx = entity.x - delta[0]
        dy = entity.y - delta[1]
        if self.map_array[dy, dx] != 1:
            entity.move(dx, dy)

    def check_tile_interaction(self):
        print(self.map_array[self.player.y, self.player.x])
        if self.map_array[self.player.y, self.player.x] == tiles.TILE_STAIRS_DOWN:
            self.load_new_level()

    def load_new_level(self):
        match self.level:
            case 1:
                self.change_map(map_gen.simplex_noise(80, 60))
            case 2:
                self.change_map(map_gen.conway(80, 60))
            case _:
                self.change_map(map_gen.random_walk(80, 60))
        self.level += 1
