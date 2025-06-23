"""
Compile bf to asm or to a Python function. Cell size is one byte.
"""

import shutil
from ctypes import CDLL
from platform import system
from typing import Callable, Iterator
from tempfile import NamedTemporaryFile

from .helpers import run_and_maybe_fail
from .tape import Tape, tape_of_size, tape_with_contents, as_tape
from .intermediate import AST, bf_to_intermediate
from .targets import Target
from .targets.jit import intermediate_to_function, UseJIT, jit_implemented


def bf_to_function(bf_code: str, *, use_jit: UseJIT = UseJIT.default()) -> Callable[[Tape], None]:
    intermediate: AST = bf_to_intermediate(bf_code)
    match use_jit:
        case UseJIT.LIBC:
            return intermediate_to_function(intermediate, linux_syscalls=False)
        case UseJIT.SYSCALLS:
            return intermediate_to_function(intermediate, linux_syscalls=True)
        case UseJIT.NO:
            with NamedTemporaryFile() as library_file:
                library_path = library_file.name
                _intermediate_to_shared(intermediate, library_path, Target.suggest())
                func = CDLL(library_path).run
                func.restype = None
                return func


def bf_to_asm(bf_code: str, *, target: Target = Target.suggest()) -> Iterator[str]:
    intermediate: AST = bf_to_intermediate(bf_code)
    yield from target.intermediate_to_asm(intermediate)


def bf_file_to_asm_file(input_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    with open(input_path) as input_file:
        bf_code = input_file.read()

    _bf_to_asm_file(bf_code, output_path, target=target)


def bf_to_shared(bf_code: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    intermediate: AST = bf_to_intermediate(bf_code)
    _intermediate_to_shared(intermediate, output_path, target)


def bf_file_to_shared(input_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    with open(input_path) as input_file:
        bf_code = input_file.read()

    bf_to_shared(bf_code, output_path, target=target)


def _intermediate_to_shared(intermediate: AST, output_path: str, target: Target) -> None:
    nasm: bool = target in (Target.X86_32_NASM, Target.X86_64_NASM, Target.X86_64_LINUX_SYSCALLS_NASM)
    if not shutil.which("cc"):
        raise RuntimeError("cc not found")
    if nasm and not shutil.which("nasm"):
        raise RuntimeError("nasm not found")

    with (NamedTemporaryFile(suffix=".s") as asm_file,
          NamedTemporaryFile(suffix=".o") as object_file):
        asm_path, object_path = asm_file.name, object_file.name
        _intermediate_to_asm_file(intermediate, asm_path, target=target)
        # assemble:
        if nasm:
            bits = 32 if target == Target.X86_32_NASM else 64
            FORMAT = "-felf" + str(bits)
            run_and_maybe_fail("nasm", FORMAT, asm_path, "-o", object_path)
        else:
            run_and_maybe_fail("cc", "-c", asm_path, "-o", object_path)
        # link:
        SHARED = "-dynamiclib" if system() == "Darwin" else "-shared"
        run_and_maybe_fail("cc", "-z", "noexecstack", SHARED, object_path, "-o", output_path)


def _intermediate_to_asm_file(intermediate: AST, output_path: str, target: Target) -> None:
    lines = target.intermediate_to_asm(intermediate)

    with open(output_path, 'w') as output_file:
        print(*lines, sep="\n", file=output_file)


def _bf_to_asm_file(bf_code: str, output_path: str, target: Target) -> None:
    lines = bf_to_asm(bf_code, target=target)

    with open(output_path, 'w') as output_file:
        print(*lines, sep="\n", file=output_file)
