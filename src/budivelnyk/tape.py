import ctypes
from typing import TypeAlias


Tape: TypeAlias = ctypes.Array[ctypes.c_byte] # TODO: make a class


def create_tape(cells: int | bytes) -> Tape: # TODO: document
    if isinstance(cells, int):
        size = cells
        return (ctypes.c_byte * size)() # TODO: is it always filled with zeros?
    else:
        size = len(cells)
        return (ctypes.c_byte * size).from_buffer_copy(cells)
