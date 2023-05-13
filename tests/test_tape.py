from array import array
import pytest
import budivelnyk as bd


def test_cast_bytes():
    x = b"\x00"
    with pytest.raises(TypeError, match="not writable"):
        bd.as_tape(x, size=1)


def test_cast_bytearray():
    x = bytearray(b"\x00")
    bd.as_tape(x, size=1)


def test_cast_int_array():
    x = array('i', [1,2,3])
    assert len(bd.as_tape(x)) == 3
    assert len(bd.as_tape(x, 6)) == 6


def test_copy_bytes():
    x = b"\x00"
    bd.make_tape(x)


def test_copy_bytearray():
    x = bytearray(b"\x00")
    with pytest.raises(TypeError, match="expected int or bytes, got bytearray"):
        bd.make_tape(x)
