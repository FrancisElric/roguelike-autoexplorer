import numpy as np
import random
import tcod

WIDTH, HEIGHT = 80, 60
MAP_SHAPE = (WIDTH, HEIGHT)
MAP_NOISE = tcod.noise.Noise(
    dimensions=2,
    algorithm=tcod.noise.Algorithm.SIMPLEX,
    seed=random.randint(0, 255),
)


def map_gen(offset) -> np.array:
    map_array = MAP_NOISE[
        tcod.noise.grid(shape=(HEIGHT, WIDTH), scale=0.25, offset=offset)
    ]
    map_buffer = np.zeros(
        shape=MAP_SHAPE,
        dtype=tcod.console.Console.DTYPE,
    )
    # DEBUG print(map_buffer)
    # DEBUG print(f"{np.shape(map_array)} {np.shape(map_buffer)}")
    # DEBUG free_space = 0
    with np.nditer(map_array, flags=["multi_index"]) as it:
        for x in it:
            if x[...] < -0.2:
                map_buffer["ch"][it.multi_index] = ord("#")
                map_buffer["fg"][it.multi_index] = (255, 255, 255, 255)
                map_buffer["bg"][it.multi_index] = (255, 255, 255, 255)
            else:
                map_buffer["ch"][it.multi_index] = ord(" ")

    # DEBUG c = tcod.console.Console(WIDTH, HEIGHT, order="F", buffer=map_buffer)
    # DEBUG print(c)
    return map_buffer


def main():
    offset = [0, 0]
    tileset = tcod.tileset.load_tilesheet(
        "anikki_square_8x8.png",
        16,
        16,
        tcod.tileset.CHARMAP_CP437,
    )
    console = tcod.console.Console(WIDTH, HEIGHT, order="F")
    with tcod.context.new(  # New window for a console of size columns×rows.
        columns=console.width,
        rows=console.height,
        tileset=tileset,
    ) as context:
        while True:  # Main loop, runs until SystemExit is raised.
            # console.
            console.rgb[:] = map_gen(offset)
            context.present(console)  # Show the console.
            # This event loop will wait until at least one event is processed before exiting.
            # For a non-blocking event loop replace `tcod.event.wait` with `tcod.event.get`.
            for event in tcod.event.wait():
                context.convert_event(event)  # Sets tile coordinates for mouse events.
                # DEBUG print(event)  # Print event names and attributes.
                match event:
                    case tcod.event.Quit():
                        raise SystemExit
                    case tcod.event.KeyDown(sym=tcod.event.KeySym.LEFT):
                        offset[1] -= 1
                    case tcod.event.KeyDown(sym=tcod.event.KeySym.RIGHT):
                        offset[1] += 1
                    case tcod.event.KeyDown(sym=tcod.event.KeySym.UP):
                        offset[0] -= 1
                    case tcod.event.KeyDown(sym=tcod.event.KeySym.DOWN):
                        offset[0] += 1


if __name__ == "__main__":
    main()
