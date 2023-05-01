import ctypes
import pytest
import budivelnyk as bd
from helpers import library_path, skip_if_jit_not_implemented


@pytest.fixture
def nop_in_dll(tmp_path, library_path):
    bd.bf_to_shared("", library_path)
    return ctypes.CDLL(library_path).run


@pytest.fixture
def nop_in_memory():
    return bd.bf_to_function("")


def test_dll_with_our_tape(nop_in_dll):
    tape = bd.create_tape(1)
    assert tape._type_ is ctypes.c_ubyte
    nop_in_dll(tape)


@skip_if_jit_not_implemented
def test_jit_with_our_tape(nop_in_memory):
    tape = bd.create_tape(1)
    assert tape._type_ is ctypes.c_ubyte
    nop_in_memory(tape)


def test_dll_with_bytes(nop_in_dll):
    tape = b"\x00"
    nop_in_dll(tape)


@skip_if_jit_not_implemented
def test_jit_with_bytes(nop_in_memory):
    tape = b"\x00"
    with pytest.raises(ctypes.ArgumentError):
        nop_in_memory(tape)
    with pytest.raises(TypeError, match="not writable"):
        nop_in_memory(bd.as_tape(tape, size=1))
    nop_in_memory(bd.create_tape(tape))


def test_dll_with_c_bytes(nop_in_dll):
    tape = (ctypes.c_byte * 1)()
    assert tape._type_ is ctypes.c_byte
    nop_in_dll(tape)


@skip_if_jit_not_implemented
def test_jit_with_c_bytes(nop_in_memory):
    tape = (ctypes.c_byte * 1)()
    assert tape._type_ is ctypes.c_byte
    with pytest.raises(ctypes.ArgumentError):
        nop_in_memory(tape)
    nop_in_memory(bd.as_tape(tape, size=1))


def test_dll_with_chars(nop_in_dll):
    tape = ctypes.create_string_buffer(1)
    assert tape._type_ is ctypes.c_char
    nop_in_dll(tape)


@skip_if_jit_not_implemented
def test_jit_with_chars(nop_in_memory):
    nop_in_memory.argtypes = None
    tape = ctypes.create_string_buffer(1)
    assert tape._type_ is ctypes.c_char
    with pytest.raises(ctypes.ArgumentError):
        nop_in_memory(tape)
    nop_in_memory(bd.as_tape(tape, size=1))
