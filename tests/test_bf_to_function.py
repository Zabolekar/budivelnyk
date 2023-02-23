from budivelnyk import bf_to_function, create_tape
from budivelnyk.targets.jit import jit_compiler_implemented
import pytest


jit_not_implemented = not jit_compiler_implemented()
skip_if_jit_not_implemented = pytest.mark.skipif(
    jit_not_implemented,
    reason="JIT compiler not implemented for this platform"
)


@skip_if_jit_not_implemented
def test_simple():
    func = bf_to_function(">+>++")
    tape = create_tape(3)
    func(tape)
    assert tape[:] == [0, 1, 2]


@skip_if_jit_not_implemented
def test_clear():
    func = bf_to_function("[-]")
    tape = create_tape(b"a")
    func(tape)
    assert tape[:] == [0]


@skip_if_jit_not_implemented
def test_multiply():
    func = bf_to_function("++[>+++<-]>[<+++++>-]")
    tape = create_tape(2)
    func(tape)
    assert tape[:] == [30, 0]


@skip_if_jit_not_implemented
def test_empty_loop():
    func = bf_to_function("[]")
    tape = create_tape(bytes([0, 123]))
    func(tape)
    assert tape[:] == [0, 123]
