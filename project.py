import tcod
import game.map_generation as map_gen
from game.engine import Engine
from game.entity import Entity
from game.map_renderer import render_map

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

    # Create a map
    map_array = map_gen.pre_made(80, 60, "prefabs/map_1.txt")
    map_rgb = render_map(map_array)
    map_type = "pre-made"

    # Create player
    player_x, player_y = map_gen.spawn_point(map_array)
    player = Entity(player_x, player_y, "☺", (255, 255, 0))

    # Create engine instance
    engine = Engine(map_array, map_rgb, player)

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
        while True:
            console.print(
                x=0,
                y=0,
                text=map_type,
                fg=(255, 255, 255),
                bg=(100, 100, 100),
            )
            engine.render(context, console)

            # This event loop will wait until at least one event is processed before exiting.
            # For a non-blocking event loop replace `tcod.event.wait` with `tcod.event.get`.
            for event in tcod.event.wait():
                context.convert_event(event)  # Sets tile coordinates for mouse events.
                # DEBUG print(event)  # Print event names and attributes.
                engine.event_handling(event)


if __name__ == "__main__":
    main()
