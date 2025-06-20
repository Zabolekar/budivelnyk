from __future__ import annotations
import enum
import platform
from typing import Iterator

from ..intermediate import AST
from .arm32 import generate_arm32
from .arm64 import generate_arm64
from .ppc32 import generate_ppc32
from .riscv64 import generate_riscv64
from .x86_32_att import generate_x86_32_att
from .x86_32_intel import generate_x86_32_gas_intel, generate_x86_32_nasm
from .x86_64_att import generate_x86_64_att
from .x86_64_intel import generate_x86_64_gas_intel, generate_x86_64_nasm

# platform.machine can be not specific enough on NetBSD,
# platform.processor can be empty on Linux, so we have
# to handle the systems differently:

def _linux_candidates(machine: str) -> tuple[Target, ...]:
    match machine:
        case "armv7l":
            return (Target.ARM32_THUMB, Target.ARM32)
        case "i686":
            return (Target.X86_32_GAS_INTEL, Target.X86_32_GAS_ATT, Target.X86_64_NASM)
        case "riscv64":
            return (Target.RISCV64,)
        case "x86_64":
            return (Target.X86_64_GAS_INTEL, Target.X86_64_LINUX_SYSCALLS_GAS_INTEL,
                    Target.X86_64_GAS_ATT, Target.X86_64_LINUX_SYSCALLS_GAS_ATT,
                    Target.X86_64_NASM, Target.X86_64_LINUX_SYSCALLS_NASM)
        case _:
            raise NotImplementedError(f"Linux on {machine} is not supported")


def _bsd_candidates(system: str, processor: str) -> tuple[Target, ...]:
    match processor:
        case "aarch64":  # tested with Net and Open
            return (Target.ARM64,)
        case "amd64":  # tested with Free
            return (Target.X86_64_GAS_INTEL, Target.X86_64_GAS_ATT, Target.X86_64_NASM)
        case "earmv7hf":  # tested with Net
            return (Target.ARM32_THUMB, Target.ARM32)
        case "i386":  # tested with Open
            return (Target.X86_32_GAS_INTEL, Target.X86_32_GAS_ATT, Target.X86_32_NASM)
        case "powerpc":  # tested with Mac OS X
            return (Target.PPC32,)
        case _:
            raise NotImplementedError(f"{system} on {processor} is not supported")


class Target(enum.Enum):
    ARM32 = enum.auto()
    ARM32_THUMB = enum.auto()
    ARM64 = enum.auto()
    PPC32 = enum.auto()
    RISCV64 = enum.auto()
    X86_32_GAS_ATT = enum.auto()
    X86_32_GAS_INTEL = enum.auto()
    X86_32_NASM = enum.auto()
    X86_64_GAS_ATT = enum.auto()
    X86_64_GAS_INTEL = enum.auto()
    X86_64_NASM = enum.auto()
    X86_64_LINUX_SYSCALLS_GAS_ATT = enum.auto()
    X86_64_LINUX_SYSCALLS_GAS_INTEL = enum.auto()
    X86_64_LINUX_SYSCALLS_NASM = enum.auto()

    @staticmethod
    def candidates() -> tuple[Target, ...]:
        system = platform.system()
        match system:
            case "Linux":
                return _linux_candidates(platform.machine())
            case "NetBSD" | "OpenBSD" | "FreeBSD" | "Darwin":
                return _bsd_candidates(system, platform.processor())
            case _:
                raise NotImplementedError(f"unsupported or unknown OS: {system}")

    @staticmethod
    def suggest() -> Target:
        return Target.candidates()[0]

    def intermediate_to_asm(self, intermediate: AST) -> Iterator[str]:
        match self:
            case Target.ARM32:
                yield from generate_arm32(intermediate, thumb=False)
            case Target.ARM32_THUMB:
                yield from generate_arm32(intermediate, thumb=True)
            case Target.ARM64:
                yield from generate_arm64(intermediate)
            case Target.PPC32:
                yield from generate_ppc32(intermediate)
            case Target.RISCV64:
                yield from generate_riscv64(intermediate)
            case Target.X86_32_GAS_ATT:
                yield from generate_x86_32_att(intermediate)
            case Target.X86_32_GAS_INTEL:
                yield from generate_x86_32_gas_intel(intermediate)
            case Target.X86_32_NASM:
                yield from generate_x86_32_nasm(intermediate)
            case Target.X86_64_GAS_ATT:
                yield from generate_x86_64_att(intermediate, linux_syscalls=False)
            case Target.X86_64_GAS_INTEL:
                yield from generate_x86_64_gas_intel(intermediate, linux_syscalls=False)
            case Target.X86_64_NASM:
                yield from generate_x86_64_nasm(intermediate, linux_syscalls=False)
            case Target.X86_64_LINUX_SYSCALLS_GAS_ATT:
                yield from generate_x86_64_att(intermediate, linux_syscalls=True)
            case Target.X86_64_LINUX_SYSCALLS_GAS_INTEL:
                yield from generate_x86_64_gas_intel(intermediate, linux_syscalls=True)
            case Target.X86_64_LINUX_SYSCALLS_NASM:
                yield from generate_x86_64_nasm(intermediate, linux_syscalls=True)
            case _:
                raise RuntimeError(f"unhandled target {self}, this is a bug")
