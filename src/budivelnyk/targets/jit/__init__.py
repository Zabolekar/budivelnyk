import mmap
import ctypes
import platform
from typing import Callable

from ...tape import Tape
from ...intermediate import AST
from .x86_64 import generate_x86_64


def _find_jit_compiler() -> Callable[[AST], bytes]:
    # see also dispatching code in targets/__init__.py

    system = platform.system()
    if system != "Linux":
        raise NotImplementedError(f"JIT is not implemented for {system}")

    machine = platform.machine()
    if machine != "x86_64":
        raise NotImplementedError(f"JIT is not implemented for Linux on {machine}")

    return generate_x86_64


jit_implemented: bool
try:
    _find_jit_compiler()
    jit_implemented = True
except NotImplementedError:
    jit_implemented = False


def _intermediate_to_machine_code(intermediate: AST) -> bytes:
    compiler = _find_jit_compiler()
    return compiler(intermediate)


def _machine_code_to_function(code: bytes) -> Callable[[Tape], None]:
    size = len(code)
    memory = _executable_memory(size)
    memory.write(code)
    array_t = ctypes.c_byte * size
    array_view = array_t.from_buffer(memory)
    return ctypes.cast(array_view, ctypes.CFUNCTYPE(None))


def intermediate_to_function(intermediate: AST) -> Callable[[Tape], None]:
    code: bytes = _intermediate_to_machine_code(intermediate)
    return _machine_code_to_function(code)


def _executable_memory(size: int) -> mmap.mmap:
    permissions = mmap.PROT_READ|mmap.PROT_WRITE|mmap.PROT_EXEC
    flags = mmap.MAP_PRIVATE|mmap.MAP_ANON
    return mmap.mmap(-1, size, flags, permissions)
