import ctypes
from typing import Any

from ...tape import create_tape

# Revealed types like ctypes._FuncPointer don't exist at runtime,
# so we have to either use Any or `if not TYPE_CHECKING` :(
def _encode_pointer(pointer: Any) -> bytes:
    pointer_size = ctypes.sizeof(pointer)
    array = create_tape(pointer_size)
    ctypes.memmove(array, ctypes.byref(pointer), pointer_size)
    return bytes(array)


def print_char(i: int) -> None:
    print(chr(i), end="")
