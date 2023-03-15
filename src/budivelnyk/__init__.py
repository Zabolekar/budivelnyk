"""
Compile bf to asm or to a Python function. Cell size is one byte.
"""

import enum
import subprocess
from os import path
from ctypes import CDLL
from warnings import warn
from typing import Callable, Iterator
from tempfile import TemporaryDirectory

from .tape import Tape, create_tape, as_tape
from .intermediate import AST, bf_to_intermediate
from .targets import Target
from .targets.jit import intermediate_to_function, jit_compiler_implemented


class UseJIT(enum.Enum):
    TRUE = enum.auto()  # attempt to use, raise exception if not implemented
    FALSE = enum.auto()  # do not attempt to use
    IF_AVAILABLE = enum.auto()  # check whether implemented, use if implemented

    def __bool__(self) -> bool:
        match self:
            case UseJIT.TRUE:
                return True
            case UseJIT.FALSE:
                return False
            case UseJIT.IF_AVAILABLE:
                return jit_compiler_implemented()


# TODO: some tape tests fail without JIT due to less strict type requirements
# TODO: document
def bf_to_function(bf_code: str, use_jit: UseJIT = UseJIT.IF_AVAILABLE) -> Callable[[Tape], None]:    
    if use_jit:
        intermediate: AST = bf_to_intermediate(bf_code)
        return intermediate_to_function(intermediate)
    else:
        with TemporaryDirectory() as tmpdir:
            asm = path.join(tmpdir, "tmp.s")
            library = path.join(tmpdir, "libtmp.so")
            bf_to_shared(bf_code, asm, library)
            return CDLL(library).run


def bf_to_asm(bf_code: str, *, target: Target = Target.suggest()) -> Iterator[str]:
    intermediate: AST = bf_to_intermediate(bf_code)
    yield from target.intermediate_to_asm(intermediate)


def bf_to_asm_file(bf_code: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    lines = bf_to_asm(bf_code, target=target)

    with open(output_path, 'w') as output_file:
        print(*lines, sep="\n", file=output_file)


def bf_file_to_asm_file(input_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    with open(input_path) as input_file:
        bf_code = input_file.read()

    bf_to_asm_file(bf_code, output_path, target=target)


def bf_to_shared(bf_code: str, asm_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    bf_to_asm_file(bf_code, asm_path, target=target)
    asm_to_shared = ["cc", "-shared", "-o", output_path, asm_path]
    process = subprocess.run(asm_to_shared, capture_output=True)
    stdout = process.stdout.decode(errors='replace')
    stderr = process.stderr.decode(errors='replace')
    if stdout:
        print(stdout)
    if stderr:
        if process.returncode == 0:
            warn(stderr, RuntimeWarning)
        else:
            raise RuntimeError(stderr)


def bf_file_to_shared(input_path: str, asm_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    with open(input_path) as input_file:
        bf_code = input_file.read()

    bf_to_shared(bf_code, asm_path, output_path, target=target)
