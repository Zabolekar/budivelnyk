import ctypes
import pytest
import budivelnyk as bd
from helpers import library_path, skip_if_jit_not_implemented


@pytest.fixture
def nop_in_dll(tmp_path, library_path):
    return bd.bf_to_function("", use_jit=False)


@pytest.fixture
def nop_in_memory():
    return bd.bf_to_function("")


def test_dll_with_our_tape(nop_in_dll):
    tape = bd.make_tape(1)
    assert tape._type_ is ctypes.c_ubyte
    nop_in_dll(tape)


@skip_if_jit_not_implemented
def test_jit_with_our_tape(nop_in_memory):
    tape = bd.make_tape(1)
    assert tape._type_ is ctypes.c_ubyte
    nop_in_memory(tape)


def test_dll_with_as_tape(nop_in_dll):
    array = bytearray(b"\x00")
    tape = bd.as_tape(array, size=1)
    assert tape._type_ is ctypes.c_ubyte
    nop_in_dll(bd.as_tape(tape, size=1))


@skip_if_jit_not_implemented
def test_jit_with_as_tape(nop_in_memory):
    array = bytearray(b"\x00")
    tape = bd.as_tape(array, size=1)
    assert tape._type_ is ctypes.c_ubyte
    nop_in_memory()


def test_dll_with_bytes(nop_in_dll):
    tape = b"\x00"
    nop_in_dll(tape)


@skip_if_jit_not_implemented
def test_jit_with_bytes(nop_in_memory):
    tape = b"\x00"
    nop_in_memory(bd.make_tape(tape))


def test_dll_with_c_bytes(nop_in_dll):
    tape = (ctypes.c_byte * 1)()
    assert tape._type_ is ctypes.c_byte
    nop_in_dll(tape)


@skip_if_jit_not_implemented
def test_jit_with_c_bytes(nop_in_memory):
    tape = (ctypes.c_byte * 1)()
    assert tape._type_ is ctypes.c_byte
    nop_in_memory(tape)


def test_dll_with_chars(nop_in_dll):
    tape = ctypes.create_string_buffer(1)
    assert tape._type_ is ctypes.c_char
    nop_in_dll(tape)


@skip_if_jit_not_implemented
def test_jit_with_chars(nop_in_memory):
    tape = ctypes.create_string_buffer(1)
    assert tape._type_ is ctypes.c_char
    nop_in_memory(bd.as_tape(tape, size=1))
