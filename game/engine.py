import tcod


class Engine:
    def __init__(self, map_array, map_buffer, player, entities=()):
        self.map_array = map_array
        self.map_buffer = map_buffer
        self.player = player
        self.entities = entities

    def event_handling(self, event):
        match event:
            case tcod.event.Quit():
                raise SystemExit
            # case tcod.event.KeyDown(sym=tcod.event.KeySym.R):
            #     if map_type == "drunkards":
            #         map_type = "noise"
            #         engine.ch
            #         map = render_map(map_caves_noise.map_gen(WIDTH, HEIGHT))
            #     elif map_type == "noise":
            #         map_type = "conway"
            #         map = render_map(map_caves_conway.map_gen(WIDTH, HEIGHT))
            #     elif map_type == "conway":
            #         map_type = "pre-made-map_2"
            #         map = render_map(
            #             map_load_premade.map_gen(WIDTH, HEIGHT, "prefabs/map_1.txt")
            #         )
            #     else:
            #         map_type = "drunkards"
            #         map = render_map(map_caves_drunkards_walk.map_gen(WIDTH, HEIGHT))

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

    def change_map(self, map_array, map_buffer):
        self.map_array = map_array
        self.map_buffer = map_buffer
