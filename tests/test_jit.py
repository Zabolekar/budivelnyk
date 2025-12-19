from budivelnyk import Bf, tape_of_size, tape_with_contents, jit_implemented
from helpers import JIT_NOT_IMPLEMENTED_MESSAGE
import pytest


if not jit_implemented:
    pytest.skip(reason=JIT_NOT_IMPLEMENTED_MESSAGE, allow_module_level=True)


def test_simple():
    func = Bf.to_function(">+>++")
    tape = tape_of_size(3)
    func(tape)
    assert tape[:] == [0, 1, 2]


def test_clear():
    func = Bf.to_function("[-]")
    tape = tape_with_contents(b"a")
    func(tape)
    assert tape[:] == [0]


def test_multiply():
    func = Bf.to_function("++[>+++<-]>[<+++++>-]")
    tape = tape_of_size(2)
    func(tape)
    assert tape[:] == [30, 0]


def test_empty_loop():
    func = Bf.to_function("[]")
    tape = tape_with_contents(bytes([0, 123]))
    func(tape)
    assert tape[:] == [0, 123]
