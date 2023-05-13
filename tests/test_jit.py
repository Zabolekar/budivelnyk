from budivelnyk import bf_to_function, make_tape
from helpers import skip_if_jit_not_implemented


@skip_if_jit_not_implemented
def test_simple():
    func = bf_to_function(">+>++")
    tape = make_tape(3)
    func(tape)
    assert tape[:] == [0, 1, 2]


@skip_if_jit_not_implemented
def test_clear():
    func = bf_to_function("[-]")
    tape = make_tape(b"a")
    func(tape)
    assert tape[:] == [0]


@skip_if_jit_not_implemented
def test_multiply():
    func = bf_to_function("++[>+++<-]>[<+++++>-]")
    tape = make_tape(2)
    func(tape)
    assert tape[:] == [30, 0]


@skip_if_jit_not_implemented
def test_empty_loop():
    func = bf_to_function("[]")
    tape = make_tape(bytes([0, 123]))
    func(tape)
    assert tape[:] == [0, 123]
