from ctypes import Array, POINTER, c_ubyte
from typing import TypeAlias, no_type_check, Callable


Tape: TypeAlias = Array[c_ubyte]
Head: TypeAlias = POINTER(c_ubyte)  # type: ignore[valid-type]
Machine: TypeAlias = Callable[[Tape|Head], Head]


def tape_of_size(size: int) -> Tape:
    return (c_ubyte * size)()


def tape_with_contents(cells: bytes|bytearray) -> Tape:
    size = len(cells)
    return (c_ubyte * size).from_buffer_copy(cells)


@no_type_check  # TODO: try collections.abc.Buffer with 3.12
def as_tape(buffer, size: int) -> Tape:
    return (c_ubyte * size).from_buffer(buffer)
