import ctypes
import pytest
import budivelnyk as bd
from helpers import generate_paths, skip_if_jit_not_implemented


@pytest.fixture
def nop_dll(tmp_path):
    asm, library = generate_paths(tmp_path, "nop")
    bd.bf_to_shared("", asm, library)
    return ctypes.CDLL(library)


def test_dll_with_our_tape(nop_dll):
    f = nop_dll.run
    tape = bd.create_tape(1)
    assert tape._type_ is ctypes.c_ubyte
    f(tape)


@skip_if_jit_not_implemented
def test_jit_with_our_tape():
    f = bd.bf_to_function("")
    tape = bd.create_tape(1)
    assert tape._type_ is ctypes.c_ubyte
    f(tape)


def test_dll_with_bytes(nop_dll):
    f = nop_dll.run
    tape = b"\x00"
    f(tape)


@skip_if_jit_not_implemented
def test_jit_with_bytes():
    f = bd.bf_to_function("")
    tape = b"\x00"
    with pytest.raises(ctypes.ArgumentError):
        f(tape)
    with pytest.raises(TypeError, match="not writable"):
        f(bd.as_tape(tape, size=1))
    f(bd.create_tape(tape))


def test_dll_with_c_bytes(nop_dll):
    f = nop_dll.run
    tape = (ctypes.c_byte * 1)()
    assert tape._type_ is ctypes.c_byte
    f(tape)


@skip_if_jit_not_implemented
def test_jit_with_c_bytes():
    f = bd.bf_to_function("")
    tape = (ctypes.c_byte * 1)()
    assert tape._type_ is ctypes.c_byte
    with pytest.raises(ctypes.ArgumentError):
        f(tape)
    f(bd.as_tape(tape, size=1))


def test_dll_with_chars(nop_dll):
    f = nop_dll.run
    tape = ctypes.create_string_buffer(1)
    assert tape._type_ is ctypes.c_char
    f(tape)


@skip_if_jit_not_implemented
def test_jit_with_chars():
    f = bd.bf_to_function("")
    f.argtypes = None
    tape = ctypes.create_string_buffer(1)
    assert tape._type_ is ctypes.c_char
    with pytest.raises(ctypes.ArgumentError):
        f(tape)
    f(bd.as_tape(tape, size=1))
