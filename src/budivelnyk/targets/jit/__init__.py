import mmap
import ctypes
import platform
from typing import Callable

from ...tape import Tape
from ...intermediate import AST
from .x86_64 import generate_x86_64


def find_jit_compiler() -> Callable[[AST], bytes] | str:
    "Return a function if platform is supported, error message otherwise."
    # see also dispatching code in targets/__init__.py

    system = platform.system()
    if system != "Linux":
        return f"unsupported or unknown OS: {system}"

    machine = platform.machine()
    if machine != "x86_64":
        return f"Linux on {machine} is not supported"

    return generate_x86_64


def _intermediate_to_machine_code(intermediate: AST) -> bytes | str:
    compiler = find_jit_compiler()
    if callable(compiler):
        return compiler(intermediate)
    else:
        raise RuntimeError(compiler)


def _machine_code_to_function(code: bytes) -> Callable[[Tape], None]:
    size = len(code)
    memory = _executable_memory(size)
    memory.write(code)
    array_t = ctypes.c_byte * size
    array_view = array_t.from_buffer(memory)
    return ctypes.cast(array_view, _functype)


def intermediate_to_function(intermediate: AST) -> Callable[[Tape], None]:
    code: bytes = _intermediate_to_machine_code(intermediate)
    return _machine_code_to_function(code)


_ubyte_p = ctypes.POINTER(ctypes.c_ubyte)
_functype = ctypes.CFUNCTYPE(None, _ubyte_p)


def _executable_memory(size: int) -> mmap.mmap:
    permissions = mmap.PROT_READ|mmap.PROT_WRITE|mmap.PROT_EXEC
    flags = mmap.MAP_PRIVATE|mmap.MAP_ANON
    return mmap.mmap(-1, size, flags, permissions)
