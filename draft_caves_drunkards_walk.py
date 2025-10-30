import random
from pickle import GLOBAL

import numpy as np
import tcod

WIDTH, HEIGHT = 80, 60
MAP_SHAPE = (WIDTH, HEIGHT)
DURATION = 50
DRUNKARDS = 15
STRAIGHT_TIMER = 3

map_array = np.ones(MAP_SHAPE)
map_buffer = np.zeros(
    shape=MAP_SHAPE,
    dtype=tcod.console.Console.DTYPE,
)
visited_cords = []


def random_direction() -> tuple[int, int]:
    x, y = (0, 0)
    match random.randint(1, 4):
        case 1:
            x += 1
        case 2:
            x -= 1
        case 3:
            y += 1
        case 4:
            y -= 1
    return x, y


def dig(x, y):
    try:  # orzech forgive me for i have sinned nyaaa~~
        # TODO don't use try here :3 nyaaaa~~
        x += dx
        y += dy
        map_array[x, y] = 0
    except IndexError:
        pass
    if (x, y) not in visited_cords:
        visited_cords.append((x, y))
    return x, y


x, y = int(WIDTH / 2), int(HEIGHT / 2)
for _ in range(DRUNKARDS):
    for _ in range(DURATION):
        print(x, y)
        # map_array[x, y] = 0
        # if (x, y) not in visited_cords:
        #     visited_cords.append((x, y))
        dx, dy = random_direction()
        if random.randint(1, 15) == 1:
            for _ in range(STRAIGHT_TIMER):
                x, y = dig(x, y)
        else:
            x, y = dig(x, y)
    x, y = random.choice(visited_cords)

with np.nditer(map_array, flags=["multi_index"]) as it:
    for x in it:
        if x[...] == 1:
            map_buffer["ch"][it.multi_index] = ord("#")
            map_buffer["fg"][it.multi_index] = (255, 255, 255, 255)
            map_buffer["bg"][it.multi_index] = (0, 0, 0, 0)
        else:
            map_buffer["ch"][it.multi_index] = ord(" ")

c = tcod.console.Console(WIDTH, HEIGHT, order="F", buffer=map_buffer)
print(c)


def main():
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
            console.rgb[...] = map_buffer
            context.present(console)  # Show the console.
            # This event loop will wait until at least one event is processed before exiting.
            # For a non-blocking event loop replace `tcod.event.wait` with `tcod.event.get`.
            for event in tcod.event.wait():
                context.convert_event(event)  # Sets tile coordinates for mouse events.
                # DEBUG print(event)  # Print event names and attributes.
                match event:
                    case tcod.event.Quit():
                        raise SystemExit


if __name__ == "__main__":
    main()
