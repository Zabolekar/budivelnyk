from array import array
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
    x = array('i', [12,34,56])
    accidentally_wrong_tape = bd.as_tape(x)
    intentionally_wrong_tape = bd.as_tape(x, 6)
    correct_tape = bd.as_tape(x, 12)
    assert accidentally_wrong_tape[:] == [12, 0, 0]
    assert intentionally_wrong_tape[:] == [12, 0, 0, 0, 34, 0]
    assert correct_tape[:] == [12, 0, 0, 0, 34, 0, 0, 0, 56, 0, 0, 0]


def test_copy_bytes():
    x = b"\x12\x34\x56"
    tape = bd.make_tape(x)
    assert tape[:] == [0x12, 0x34, 0x56]


def test_copy_bytearray():
    x = bytearray(b"\x00")
    with pytest.raises(TypeError, match="expected int or bytes, got bytearray"):
        bd.make_tape(x)
