import ctypes
from typing import TypeAlias


Tape: TypeAlias = ctypes.Array[ctypes.c_ubyte]


def create_tape(cells: int | bytes) -> Tape:
    if isinstance(cells, int):
        size = cells
        return (ctypes.c_ubyte * size)()
    else:
        size = len(cells)
        return (ctypes.c_ubyte * size).from_buffer_copy(cells)


def as_tape(buffer, size=None) -> Tape:  # type: ignore
    if size is None:
        size = len(buffer)
    return (ctypes.c_ubyte * size).from_buffer(buffer)
