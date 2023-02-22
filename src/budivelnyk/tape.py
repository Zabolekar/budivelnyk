import ctypes
from typing import TypeAlias

Tape: TypeAlias = ctypes.Array[ctypes.c_ubyte]

def create_tape(cells: int | bytes) -> Tape: # TODO: document
    if isinstance(cells, int):
        size = cells
        return (ctypes.c_ubyte * size)()
    else:
        size = len(cells)
        return (ctypes.c_ubyte * size).from_buffer_copy(cells)


def as_tape(cells) -> Tape:  # type: ignore
    size = len(cells)
    return (ctypes.c_ubyte * size).from_buffer(cells)
