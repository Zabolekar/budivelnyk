import ctypes
from typing import TypeAlias, no_type_check


Tape: TypeAlias = ctypes.Array[ctypes.c_ubyte]


def tape_of_size(size: int) -> Tape:
    return (ctypes.c_ubyte * size)()


def tape_with_contents(cells: bytes|bytearray) -> Tape:
    size = len(cells)
    return (ctypes.c_ubyte * size).from_buffer_copy(cells)


@no_type_check  # TODO: try collections.abc.Buffer with 3.12
def as_tape(buffer, size: int) -> Tape:
    return (ctypes.c_ubyte * size).from_buffer(buffer)
