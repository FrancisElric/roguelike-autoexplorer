import tcod
import draft_caves_noise
import draft_caves_drunkards_walk
import draft_caves_conway
import numpy as np

WIDTH, HEIGHT = 80, 60  # Console width and height in tiles.
# width ->>>>
# height -^^^^


def main() -> None:
    """Script entry point."""

    # Load the font, 16 by 16, using DF layout
    # Font source: https://dwarffortresswiki.org/index.php/Tileset_repository#1.C3.971
    tileset = tcod.tileset.load_tilesheet(
        "anikki_square_8x8.png",
        16,
        16,
        tcod.tileset.CHARMAP_CP437,
    )
    map = draft_caves_conway.map_gen(WIDTH, HEIGHT)
    map_type = "conway"
    # Create the main console.
    console = tcod.console.Console(WIDTH, HEIGHT)

    # Create a window based on this console and tileset.
    with tcod.context.new(  # New window for a console of size columns×rows.
        columns=console.width, rows=console.height, tileset=tileset, title="nyaaa~~"
    ) as context:
        while True:  # Main loop, runs until SystemExit is raised.
            console.clear()
            console.rgb[:] = map
            console.print(
                x=0,
                y=0,
                text=map_type,
                fg=(255, 255, 255),
                bg=(100, 100, 100),
            )
            context.present(console)  # Show the console.

            # This event loop will wait until at least one event is processed before exiting.
            # For a non-blocking event loop replace `tcod.event.wait` with `tcod.event.get`.
            for event in tcod.event.wait():
                context.convert_event(event)  # Sets tile coordinates for mouse events.
                # DEBUG print(event)  # Print event names and attributes.
                match event:
                    case tcod.event.Quit():
                        raise SystemExit
                    case tcod.event.KeyDown(sym=tcod.event.KeySym.R):
                        if map_type == "drunkards":
                            map_type = "noise"
                            map = draft_caves_noise.map_gen(WIDTH, HEIGHT)
                        elif map_type == "noise":
                            map_type = "conway"
                            map = draft_caves_conway.map_gen(WIDTH, HEIGHT)
                        else:
                            map_type = "drunkards"
                            map = draft_caves_drunkards_walk.map_gen(WIDTH, HEIGHT)

        # The window will be closed after the above with-block exits.


if __name__ == "__main__":
    main()
