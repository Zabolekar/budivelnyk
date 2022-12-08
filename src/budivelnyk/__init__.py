"""
Compile bf to asm. Cell size is one byte.
"""

from __future__ import annotations
import enum
import subprocess
import platform
from warnings import warn
from typing import Iterator

from .intermediate import AST, bf_to_intermediate
from .x86_64_att import generate_x86_64_att
from .x86_64_intel import generate_x86_64_intel
from .arm64 import generate_arm64
from .riscv64 import generate_riscv64

class Target(enum.Enum):
    X86_64_INTEL = enum.auto()
    X86_64_ATT = enum.auto()
    ARM64 = enum.auto()
    RISCV64 = enum.auto()
    
    @staticmethod
    def suggest() -> Target:
        return Target.candidates()[0]

    @staticmethod
    def candidates() -> tuple[Target, ...]:
        system = platform.system()
        if system == "Linux":
            machine = platform.machine()
            if machine == "x86_64":
                return (Target.X86_64_INTEL, Target.X86_64_ATT)
            elif machine == "riscv64":
                return (Target.RISCV64,)
            else:
                raise RuntimeError(f"Linux on {machine} is not supported")
        elif system in ("NetBSD", "OpenBSD"):
            processor = platform.processor()
            if processor == "aarch64":
                return (Target.ARM64,)
            else:
                raise RuntimeError(f"{system} on {processor} is not supported")
        else:
            raise RuntimeError(f"unsupported or unknown OS: {system}")
        

def intermediate_to_asm(intermediate: AST, *, target: Target) -> Iterator[str]:
    if target == Target.X86_64_INTEL:
        yield from generate_x86_64_intel(intermediate)
    elif target == Target.X86_64_ATT:
        yield from generate_x86_64_att(intermediate)
    elif target == Target.ARM64:
        yield from generate_arm64(intermediate)
    elif target == Target.RISCV64:
        yield from generate_riscv64(intermediate)


def bf_to_asm(bf_code: str, *, target: Target = Target.suggest()) -> Iterator[str]:
    intermediate: AST = bf_to_intermediate(bf_code)
    yield from intermediate_to_asm(intermediate, target=target)


def bf_file_to_asm_file(input_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    with open(input_path) as input_file:
        bf_code = input_file.read()

    lines = bf_to_asm(bf_code, target=target)

    with open(output_path, 'w') as output_file:
        print(*lines, sep="\n", file=output_file)


def bf_file_to_shared(input_path: str, asm_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    bf_file_to_asm_file(input_path, asm_path, target=target)
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
