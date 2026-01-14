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


class Backend(enum.Enum):
    ARM32_LIBC_ELF_USUAL = enum.auto()
    ARM32_THUMB_LIBC_ELF_USUAL = enum.auto()
    ARM64_LIBC_ELF_USUAL = enum.auto()
    PPC32_LIBC_MACHO_USUAL = enum.auto()
    RISCV64_LIBC_ELF_USUAL = enum.auto()
    X86_32_LIBC_ELF_GAS_ATT = enum.auto()
    X86_32_LIBC_ELF_GAS_INTEL = enum.auto()
    X86_32_LIBC_ELF_NASM = enum.auto()
    X86_64_LIBC_TODO_GAS_ATT = enum.auto()
    X86_64_LIBC_TODO_GAS_INTEL = enum.auto()
    X86_64_LIBC_TODO_NASM = enum.auto()
    X86_64_LINUX_SYSCALLS_ELF_GAS_ATT = enum.auto()
    X86_64_LINUX_SYSCALLS_ELF_GAS_INTEL = enum.auto()
    X86_64_LINUX_SYSCALLS_ELF_NASM = enum.auto()

    @staticmethod
    def candidates() -> list[Backend]:
        system, machine, processor = platform.system(), platform.machine(), platform.processor()
        match system, machine, processor:
            case "Linux", "x86_64", _:
                return [Backend.X86_64_LIBC_TODO_GAS_INTEL, Backend.X86_64_LINUX_SYSCALLS_ELF_GAS_INTEL,
                        Backend.X86_64_LIBC_TODO_GAS_ATT, Backend.X86_64_LINUX_SYSCALLS_ELF_GAS_ATT,
                        Backend.X86_64_LIBC_TODO_NASM, Backend.X86_64_LINUX_SYSCALLS_ELF_NASM]
            case ("FreeBSD", "amd64", "amd64") | ("Darwin", "x86_64", _):
                return [Backend.X86_64_LIBC_TODO_GAS_INTEL, Backend.X86_64_LIBC_TODO_GAS_ATT, Backend.X86_64_LIBC_TODO_NASM]
            case ("Linux", "i686", _) | ("OpenBSD", _, "i386"):
                return [Backend.X86_32_LIBC_ELF_GAS_INTEL, Backend.X86_32_LIBC_ELF_GAS_ATT, Backend.X86_32_LIBC_ELF_NASM]
            case "NetBSD"|"OpenBSD", _, "aarch64":
                return [Backend.ARM64_LIBC_ELF_USUAL]
            case ("Linux", "armv7l", _) | ("NetBSD", _, "earmv7hf"):
                return [Backend.ARM32_LIBC_ELF_USUAL, Backend.ARM32_THUMB_LIBC_ELF_USUAL]
            case "Linux", "riscv64", _:
                return [Backend.RISCV64_LIBC_ELF_USUAL]
            case "Darwin", _, "powerpc":
                return [Backend.PPC32_LIBC_MACHO_USUAL]
            case _:
                if processor in (machine, ''):
                    hardware = machine
                else:
                    hardware = f"{machine} ({processor})"
                raise NotImplementedError(f"unsupported or unknown platform: {system} on {hardware}")

    @staticmethod
    def suggest() -> Backend:
        return Backend.candidates()[0]

    def intermediate_to_asm(self, intermediate: AST) -> Iterator[str]:
        match self:
            case Backend.ARM32_LIBC_ELF_USUAL:
                yield from generate_arm32(intermediate, thumb=False)
            case Backend.ARM32_THUMB_LIBC_ELF_USUAL:
                yield from generate_arm32(intermediate, thumb=True)
            case Backend.ARM64_LIBC_ELF_USUAL:
                yield from generate_arm64(intermediate)
            case Backend.PPC32_LIBC_MACHO_USUAL:
                yield from generate_ppc32(intermediate)
            case Backend.RISCV64_LIBC_ELF_USUAL:
                yield from generate_riscv64(intermediate)
            case Backend.X86_32_LIBC_ELF_GAS_ATT:
                yield from generate_x86_32_att(intermediate)
            case Backend.X86_32_LIBC_ELF_GAS_INTEL:
                yield from generate_x86_32_gas_intel(intermediate)
            case Backend.X86_32_LIBC_ELF_NASM:
                yield from generate_x86_32_nasm(intermediate)
            case Backend.X86_64_LIBC_TODO_GAS_ATT:
                yield from generate_x86_64_att(intermediate, linux_syscalls=False)
            case Backend.X86_64_LIBC_TODO_GAS_INTEL:
                yield from generate_x86_64_gas_intel(intermediate, linux_syscalls=False)
            case Backend.X86_64_LIBC_TODO_NASM:
                yield from generate_x86_64_nasm(intermediate, linux_syscalls=False)
            case Backend.X86_64_LINUX_SYSCALLS_ELF_GAS_ATT:
                yield from generate_x86_64_att(intermediate, linux_syscalls=True)
            case Backend.X86_64_LINUX_SYSCALLS_ELF_GAS_INTEL:
                yield from generate_x86_64_gas_intel(intermediate, linux_syscalls=True)
            case Backend.X86_64_LINUX_SYSCALLS_ELF_NASM:
                yield from generate_x86_64_nasm(intermediate, linux_syscalls=True)
            case _:
                raise RuntimeError(f"unhandled backend {self}, this is a bug")
