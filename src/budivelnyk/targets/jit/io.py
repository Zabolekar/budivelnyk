import sys
import ctypes

from ...tape import create_tape


def _reinterpret_pointer(pointer) -> bytes:  # type: ignore
    pointer_size = ctypes.sizeof(pointer)
    array = create_tape(pointer_size)
    ctypes.memmove(array, ctypes.byref(pointer), pointer_size)
    return bytes(array)


@ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)  # type: ignore
def _write_char(i: int) -> int:
    print(chr(i), end="")
    return i


@ctypes.CFUNCTYPE(ctypes.c_int)  # type: ignore
def _read_char() -> int:
    return ord(sys.stdin.read(1))


encoded_write_char: bytes = _reinterpret_pointer(_write_char)
encoded_read_char: bytes = _reinterpret_pointer(_read_char)
