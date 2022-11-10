"""
Compile bf to asm. Cell size is one byte.
"""

from __future__ import annotations
import enum
import subprocess
from typing import Iterator
from platform import machine

from .intermediate import Node, bf_to_intermediate
from .x86_64_att import generate_x86_64_att
from .x86_64_intel import generate_x86_64_intel


class Target(enum.Enum):
    X86_64_INTEL = enum.auto()
    X86_64_ATT = enum.auto()
    X86_32_INTEL = enum.auto()
    X86_32_ATT = enum.auto()
    # ARM
    ARM64 = enum.auto()
    ARM32 = enum.auto()
    # ...
    
    @staticmethod
    def suggest() -> Target:
        if machine() == "x86_64":
            return Target.X86_64_INTEL
        else:
            raise RuntimeError("unsupported or unknown architecture")

    @staticmethod
    def candidates() -> tuple[Target, ...]:
        if machine() == "x86_64":
            return (Target.X86_64_INTEL, Target.X86_64_ATT)
        else:
            raise RuntimeError("unsupported or unknown architecture")


def intermediate_to_asm(intermediate: list[Node], *, target: Target) -> Iterator[str]:
    if target == Target.X86_64_INTEL:
        yield from generate_x86_64_intel(intermediate)
    elif target == Target.X86_64_ATT:
        yield from generate_x86_64_att(intermediate)


def bf_to_asm(input_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    with open(input_path) as input_file:
        bf_code = input_file.read()

    intermediate = bf_to_intermediate(bf_code)

    with open(output_path, 'w') as output_file:
        lines = intermediate_to_asm(intermediate, target=target)
        print(*lines, sep="\n", file=output_file)


def bf_to_shared(input_path: str, asm_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    bf_to_asm(input_path, asm_path, target=target)
    asm_to_shared = ["cc", "-shared", "-o", output_path, asm_path]
    subprocess.run(asm_to_shared).check_returncode()
