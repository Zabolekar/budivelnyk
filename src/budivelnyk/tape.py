import ctypes
from typing import TypeAlias, no_type_check


Tape: TypeAlias = ctypes.Array[ctypes.c_ubyte]


def make_tape(cells: int | bytes) -> Tape:
    if isinstance(cells, int):
        size = cells
        return (ctypes.c_ubyte * size)()
    elif isinstance(cells, bytes):
        size = len(cells)
        return (ctypes.c_ubyte * size).from_buffer_copy(cells)
    else:
        raise TypeError(f"expected int or bytes, got {type(cells).__name__}")


@no_type_check
def as_tape(buffer, size=None) -> Tape:
    if size is None:
        size = len(buffer)
    return (ctypes.c_ubyte * size).from_buffer(buffer)
