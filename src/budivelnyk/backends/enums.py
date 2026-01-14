import enum


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
