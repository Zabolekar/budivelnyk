"""
Compile bf to asm or to a Python function. Cell size is one byte.
"""

from typing import Callable, Iterator

from .frontends.bf import Bf
from .backends import Backend
from .backends.jit import UseJIT, jit_implemented
from .tape import Tape, tape_of_size, tape_with_contents, as_tape


def bf_to_function(bf_code: str, *, use_jit: UseJIT = UseJIT.default()) -> Callable[[Tape], None]:
    return Bf.to_function(bf_code, use_jit=use_jit)

def bf_to_asm(bf_code: str, *, backend: Backend = Backend.suggest()) -> Iterator[str]:
    return Bf.to_asm(bf_code, backend=backend)

def bf_file_to_asm_file(input_path: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None:
    Bf.file_to_asm_file(input_path, output_path, backend=backend)

def bf_to_shared(bf_code: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None:
    Bf.to_shared(bf_code, output_path, backend=backend)

def bf_file_to_shared(input_path: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None:
    Bf.file_to_shared(input_path, output_path, backend=backend)
