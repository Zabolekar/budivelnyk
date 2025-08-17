from budivelnyk import Bf, tape_of_size, tape_with_contents
from helpers import skip_if_jit_not_implemented


@skip_if_jit_not_implemented
def test_simple():
    func = Bf.to_function(">+>++")
    tape = tape_of_size(3)
    func(tape)
    assert tape[:] == [0, 1, 2]


@skip_if_jit_not_implemented
def test_clear():
    func = Bf.to_function("[-]")
    tape = tape_with_contents(b"a")
    func(tape)
    assert tape[:] == [0]


@skip_if_jit_not_implemented
def test_multiply():
    func = Bf.to_function("++[>+++<-]>[<+++++>-]")
    tape = tape_of_size(2)
    func(tape)
    assert tape[:] == [30, 0]


@skip_if_jit_not_implemented
def test_empty_loop():
    func = Bf.to_function("[]")
    tape = tape_with_contents(bytes([0, 123]))
    func(tape)
    assert tape[:] == [0, 123]
