import tcod
import game.map_generation as map_gen
from game.engine import Engine
from game.entity import Entity
from game.map_renderer import map_array_to_rgb

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

    # Create engine instance
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
        engine.change_map("preload", "prefabs/map_1.txt")
        while True:
            engine.render()

            # This event loop will wait until at least one event is processed before exiting.
            # For a non-blocking event loop replace `tcod.event.wait` with `tcod.event.get`.
            for event in tcod.event.wait():
                # context.convert_event(event)  # Sets tile coordinates for mouse events.
                # DEBUG print(event)  # Print event names and attributes.
                engine.event_handling(event)


if __name__ == "__main__":
    main()
