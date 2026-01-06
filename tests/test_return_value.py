from budivelnyk import Bf, jit_implemented, UseJIT, tape_with_contents, Backend, shared_to_function
from helpers import JIT_NOT_IMPLEMENTED_MESSAGE, library_path 
import pytest


backends = Backend.candidates()


def common_part(func):
    contents = [12, 34]
    tape = tape_with_contents(bytes(contents))
    result = func(tape)
    assert tape[:] == contents
    assert result[0] == 34


@pytest.mark.skipif(not jit_implemented, reason=JIT_NOT_IMPLEMENTED_MESSAGE)
def test_with_jit():
    func = Bf.to_function(">", use_jit=UseJIT.LIBC)
    common_part(func)


def test_without_jit():
    func = Bf.to_function(">", use_jit=UseJIT.NO)
    common_part(func)


@pytest.mark.parametrize("backend", backends)
def test_backends(backend, library_path):
    Bf.to_shared(">", library_path, backend=backend)
    func = shared_to_function(library_path)
    common_part(func)

