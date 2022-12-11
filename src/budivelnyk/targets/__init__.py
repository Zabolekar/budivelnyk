from __future__ import annotations
import enum
import platform
from typing import Iterator

from ..intermediate import AST
from .x86_64_att import generate_x86_64_att
from .x86_64_intel import generate_x86_64_intel
from .arm64 import generate_arm64
from .riscv64 import generate_riscv64

# platform.machine can be not specific enough on NetBSD,
# platform.processor can be empty on Linux, so we have
# to handle the systems differently:

def _linux_candidates(machine: str) -> tuple[Target, ...]:
    match machine:
        case "x86_64":
            return (Target.X86_64_INTEL, Target.X86_64_ATT)
        case "riscv64":
            return (Target.RISCV64,)
        case _:
            raise RuntimeError(f"Linux on {machine} is not supported")


def _bsd_candidates(system: str, processor: str) -> tuple[Target, ...]:
    match processor:
        case "aarch64":
            return (Target.ARM64,)
        case _:
            raise RuntimeError(f"{system} on {processor} is not supported")


class Target(enum.Enum):
    X86_64_INTEL = enum.auto()
    X86_64_ATT = enum.auto()
    ARM64 = enum.auto()
    RISCV64 = enum.auto()

    @staticmethod
    def candidates() -> tuple[Target, ...]:
        system = platform.system()
        match system:
            case "Linux":
                return _linux_candidates(platform.machine())
            case "NetBSD" | "OpenBSD":
                return _bsd_candidates(system, platform.processor())
            case _:
                raise RuntimeError(f"unsupported or unknown OS: {system}")

    @staticmethod
    def suggest() -> Target:
        return Target.candidates()[0]


    def intermediate_to_asm(self, intermediate: AST) -> Iterator[str]:
        match self:
            case Target.X86_64_INTEL:
                yield from generate_x86_64_intel(intermediate)
            case Target.X86_64_ATT:
                yield from generate_x86_64_att(intermediate)
            case Target.ARM64:
                yield from generate_arm64(intermediate)
            case Target.RISCV64:
                yield from generate_riscv64(intermediate)
