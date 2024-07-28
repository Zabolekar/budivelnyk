import ctypes
import pytest
import budivelnyk as bd


@pytest.fixture(params=["DLL", "memory"])
def nop(request):
    match request.param:
        case "DLL":
            return bd.bf_to_function("", use_jit=bd.UseJIT.NO)
        case "memory":
            if not bd.jit_implemented:
                pytest.skip()
            return bd.bf_to_function("", use_jit=bd.UseJIT.SYSCALLS)    


def test_our_tape(nop):
    tape = bd.tape_of_size(1)
    assert tape._type_ is ctypes.c_ubyte
    nop(tape)


def test_as_tape(nop):
    array = bytearray(b"\x00")
    tape = bd.as_tape(array, size=1)
    assert tape._type_ is ctypes.c_ubyte
    nop(bd.as_tape(tape, size=1))


def test_bytes(nop):
    tape = b"\x00"
    nop(tape)


def test_c_bytes(nop):
    tape = (ctypes.c_byte * 1)()
    assert tape._type_ is ctypes.c_byte
    nop(tape)


def test_string_buffer(nop):
    tape = ctypes.create_string_buffer(1)
    assert tape._type_ is ctypes.c_char
    nop(tape)
