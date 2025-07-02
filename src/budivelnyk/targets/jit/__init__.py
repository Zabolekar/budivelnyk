from __future__ import annotations

import mmap
import ctypes
import platform
from enum import Enum, auto
from typing import Callable

from ...tape import Tape
from ...intermediate import AST
from .x86_64 import generate_x86_64


jit_implemented: bool = platform.system() == "Linux" and platform.machine() == "x86_64"
# see also dispatching code in targets/__init__.py


class UseJIT(Enum):
    LIBC = auto()
    SYSCALLS = auto()
    NO = auto()

    @staticmethod
    def default() -> UseJIT:
        return UseJIT.SYSCALLS if jit_implemented else UseJIT.NO


def _intermediate_to_machine_code(intermediate: AST, linux_syscalls: bool) -> bytes:
    if jit_implemented:
        return generate_x86_64(intermediate, linux_syscalls)
    else:
        raise NotImplementedError("JIT is only implemented for Linux on x86_64")


def _machine_code_to_function(code: bytes) -> Callable[[Tape], None]:
    size = len(code)
    memory = _executable_memory(size)
    memory.write(code)
    array_t = ctypes.c_byte * size
    array_view = array_t.from_buffer(memory)
    return ctypes.cast(array_view, ctypes.CFUNCTYPE(None))


def intermediate_to_function(intermediate: AST, *, linux_syscalls: bool) -> Callable[[Tape], None]:
    code: bytes = _intermediate_to_machine_code(intermediate, linux_syscalls)
    return _machine_code_to_function(code)


# TODO: error handling, especially on platforms that aren't Linux, and tests
# TODO: this is wasteful if we allocate lots of functions all smaller than os.sysconf("SC_PAGESIZE")
def _executable_memory(size: int) -> mmap.mmap:
    permissions = mmap.PROT_READ|mmap.PROT_WRITE|mmap.PROT_EXEC
    flags = mmap.MAP_PRIVATE|mmap.MAP_ANON
    return mmap.mmap(-1, size, flags, permissions)
