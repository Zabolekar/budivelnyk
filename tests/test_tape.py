from array import array
import sys
import platform
import pytest
import budivelnyk as bd


def test_cast_bytes():
    x = b"\x12\x34\x56"
    with pytest.raises(TypeError, match="not writable"):
        bd.as_tape(x, size=1)


def test_cast_bytearray():
    x = bytearray(b"\x12\x34\x56")
    tape = bd.as_tape(x, size=1)
    assert tape[:] == [0x12]


def test_cast_int_array():
    x = array('i', [12, 34, 56])
    intentionally_wrong_tape = bd.as_tape(x, len(x))
    correct_tape = bd.as_tape(x, len(x) * x.itemsize)
    if platform.machine() == "Power Macintosh":
        assert sys.byteorder == "big"
        assert intentionally_wrong_tape[:] == [0, 0, 0]
        assert correct_tape[:] == [0, 0, 0, 12, 0, 0, 0, 34, 0, 0, 0, 56]
    else:
        assert sys.byteorder == "little"
        assert intentionally_wrong_tape[:] == [12, 0, 0]
        assert correct_tape[:] == [12, 0, 0, 0, 34, 0, 0, 0, 56, 0, 0, 0]


def test_copy_bytes():
    x = b"\x12\x34\x56"
    tape = bd.tape_with_contents(x)
    assert tape[:] == [0x12, 0x34, 0x56]


def test_copy_bytearray():
    x = bytearray(b"\x12\x34\x56")
    tape = bd.tape_with_contents(x)
    assert tape[:] == [0x12, 0x34, 0x56]
