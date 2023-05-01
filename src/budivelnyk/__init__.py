"""
Compile bf to asm or to a Python function. Cell size is one byte.
"""

import enum
import shutil
from os import path
from ctypes import CDLL
from platform import system
from typing import Callable, Iterator
from tempfile import NamedTemporaryFile

from .helpers import run_and_maybe_fail
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
        with NamedTemporaryFile() as library_file:
            library_path = library_file.name
            bf_to_shared(bf_code, library_path)
            return CDLL(library_path).run


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


def bf_to_shared(bf_code: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    nasm: bool = target in (Target.X86_32_NASM, Target.X86_64_NASM)
    if not shutil.which("cc"):
        raise RuntimeError("cc not found")
    if nasm and not shutil.which("nasm"):
        raise RuntimeError("nasm not found")

    with (NamedTemporaryFile(suffix=".s") as asm_file,
          NamedTemporaryFile(suffix=".o") as object_file):
        asm_path, object_path = asm_file.name, object_file.name
        bf_to_asm_file(bf_code, asm_path, target=target)
        # assemble:
        if nasm:
            LINUX = ["-DLINUX"] if system() == "Linux" else []
            run_and_maybe_fail("nasm", "-felf64", asm_path, "-o", object_path, *LINUX)
        else:
            run_and_maybe_fail("cc", "-c", asm_path, "-o", object_path)
        # link:
        SHARED = "-dynamiclib" if system() == "Darwin" else "-shared" 
        run_and_maybe_fail("cc", SHARED, object_path, "-o", output_path)


def bf_file_to_shared(input_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    with open(input_path) as input_file:
        bf_code = input_file.read()

    bf_to_shared(bf_code, output_path, target=target)
