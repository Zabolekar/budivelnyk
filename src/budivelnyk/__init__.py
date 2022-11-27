"""
Compile bf to asm. Cell size is one byte.
"""

from __future__ import annotations
import enum
import subprocess
from typing import Iterator
from platform import system, machine, processor

from .intermediate import AST, bf_to_intermediate
from .x86_64_att import generate_x86_64_att
from .x86_64_intel import generate_x86_64_intel
from .arm64 import generate_arm64

class Target(enum.Enum):
    X86_64_INTEL = enum.auto()
    X86_64_ATT = enum.auto()
    ARM64 = enum.auto()
    
    @staticmethod
    def suggest() -> Target:
        return Target.candidates()[0]

    @staticmethod
    def candidates() -> tuple[Target, ...]:
        if system() == "Linux" and machine() == "x86_64":
            return (Target.X86_64_INTEL, Target.X86_64_ATT)
        elif system() == "NetBSD" and processor() == "aarch64":
            return (Target.ARM64,)
        else:
            raise RuntimeError("unsupported or unknown architecture")
        

def intermediate_to_asm(intermediate: AST, *, target: Target) -> Iterator[str]:
    if target == Target.X86_64_INTEL:
        yield from generate_x86_64_intel(intermediate)
    elif target == Target.X86_64_ATT:
        yield from generate_x86_64_att(intermediate)
    elif target == Target.ARM64:
        yield from generate_arm64(intermediate)

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
    subprocess.run(asm_to_shared).check_returncode()
