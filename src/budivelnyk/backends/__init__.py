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


class InstructionSet(enum.Enum):
    ARM32 = enum.auto()
    ARM32_THUMB = enum.auto()
    ARM64 = enum.auto()
    PPC32 = enum.auto()
    RISCV64 = enum.auto()
    X86_32 = enum.auto()
    X86_64 = enum.auto()


class InputOutput(enum.Enum):
    LIBC = enum.auto()
    LINUX_SYSCALLS = enum.auto()


class Format(enum.Enum):
    ELF = enum.auto()
    MACHO = enum.auto()


class Syntax(enum.Enum):
    GAS_ATT = enum.auto()
    GAS_INTEL = enum.auto()
    NASM = enum.auto()
    USUAL = enum.auto()


class Backend(enum.Enum):
    ARM32_LIBC_ELF_USUAL = "arm32-libc-elf-usual"
    ARM32_THUMB_LIBC_ELF_USUAL = "arm32_thumb-libc-elf-usual"
    ARM64_LIBC_ELF_USUAL = "arm64-libc-elf-usual"
    PPC32_LIBC_MACHO_USUAL = "ppc32-libc-macho-usual"
    RISCV64_LIBC_ELF_USUAL = "riscv64-libc-elf-usual"
    X86_32_LIBC_ELF_GAS_ATT = "x86_32-libc-elf-gas_att"
    X86_32_LIBC_ELF_GAS_INTEL = "x86_32-libc-elf-gas_intel"
    X86_32_LIBC_ELF_NASM = "x86_32-libc-elf-nasm"
    X86_64_LIBC_TODO_GAS_ATT = "x86_64-libc-elf-gas_att"
    X86_64_LIBC_TODO_GAS_INTEL = "x86_64-libc-elf-gas_intel"
    X86_64_LIBC_TODO_NASM = "x86_64-libc-elf-nasm"
    X86_64_LINUX_SYSCALLS_ELF_GAS_ATT = "x86_64-linux_syscalls-elf-gas_att"
    X86_64_LINUX_SYSCALLS_ELF_GAS_INTEL = "x86_64-linux_syscalls-elf-gas_intel"
    X86_64_LINUX_SYSCALLS_ELF_NASM = "x86_64-linux_syscalls-elf-nasm"

    def __init__(self, description: str):
        instruction_set, io, format, syntax = (token.upper() for token in description.split("-"))
        self.instruction_set = InstructionSet[instruction_set]
        self.io = InputOutput[io]
        self.format = Format[format]
        self.syntax = Syntax[syntax]

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
