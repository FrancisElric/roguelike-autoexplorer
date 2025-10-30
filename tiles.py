import numpy as np
import tcod.console

floor = (ord(" "), (255, 255, 255), (255, 255, 255))

buffer = np.zeros(
    shape=(20, 4),
    dtype=tcod.console.Console.DTYPE,
    order="F",
)
buffer[:] = floor
c = tcod.console.Console(20, 3, order="F", buffer=buffer)
print(c)
