from typing import Iterator
from platform import system

from ...intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

from .io import encoded_read_char, encoded_write_char
from .hex import b


def generate_x86_64(intermediate: AST, linux_syscalls: bool) -> bytes:
    # TODO:
    # I need JIT tests with ., and the best way to achieve it is to unify test_jit and test_bf_to_shared as test_bf_to_function.
    # Separately, there should be (less detailed) tests for the other four bf* functions.

    return b"".join([*_generate_prologue(linux_syscalls),
                     *_generate_body(intermediate, linux_syscalls),
                     *_generate_epilogue(linux_syscalls)])


def _generate_prologue(linux_syscalls: bool) -> Iterator[bytes]:
    if not linux_syscalls:
        yield b("41 54")                        # push r12
        yield b("41 55")                        # push r13
        yield b("49 BC", encoded_write_char)    # movabs r12, encoded_write_char
        yield b("49 BD", encoded_read_char)     # movabs r13, encoded_read_char


def _generate_epilogue(linux_syscalls: bool) -> Iterator[bytes]:
    if not linux_syscalls:
        yield b("41 5D")   # pop r13
        yield b("41 5C")   # pop r12
    yield b("C3")      # ret


def _generate_body(intermediate: AST, linux_syscalls: bool) -> Iterator[bytes]:
    for node in intermediate:
        match node:
            case Add(1):
                yield b("FE 07")            # inc byte ptr [rdi]
            case Add(n):
                yield b("80 07", n)     # add byte ptr [rdi], n
            case Subtract(1):
                yield b("FE 0F")            # dec byte ptr [rdi]
            case Subtract(n):
                yield b("80 2F", n)      # sub byte ptr [rdi], n
            case Forward(1):
                yield b("48 FF C7")        # inc rdi
            case Forward(n):
                yield b("48 83 C7", n)  # add rdi, n  TODO: large n
            case Back(1):
                yield b("48 FF CF")        # dec rdi
            case Back(n):
                yield b("48 83 EF", n)  # sub rdi, n  TODO: large n
            case Output(n):
                if linux_syscalls:
                    yield b("48 89 fe")        # mov rsi, rdi
                    yield b("bf 01 00 00 00")  # mov edi, 1
                    yield b("ba 01 00 00 00")  # mov edx, 1
                    
                    yield from [
                        b("b8 01 00 00 00")  # mov eax, 1
                      + b("0f 05")           # syscall
                    ] * n
                    yield b("48 89 f7")        # mov rdi, rsi
                else:
                    yield b("57")              # push rdi
                    yield b("48 0F B6 3F")     # movzx rdi, byte ptr [rdi]
                    sequence = [
                        b("41 FF D4"),         # call r12 (see prologue)
                        b("48 89 C7")          # mov rdi, rax
                    ] * n
                    yield from sequence[:-1]
                    yield b("5F")              # pop rdi
            case Input(n):
                if linux_syscalls:
                    yield b("48 89 fe")        # mov rsi, rdi
                    yield b("bf 00 00 00 00")  # mov edi, 0
                    yield b("ba 01 00 00 00")  # mov edx, 1
                    yield b("b8 00 00 00 00")  # mov eax, 0
                    yield b("0f 05")           # syscall
                    yield b("48 89 f7")        # mov rdi, rsi
                    yield b("83 f8 01")        # cmp eax, 1
                    yield b("74 03")           # je read_ok
                    yield b("c6 07 00")        # mov byte prt [rdi], 0
                    # read_ok:
                else:
                    yield b("57")              # push rdi
                    yield from [
                        b("41 FF D5")          # call r13 (see prologue)
                    ] * n
                    yield b("5F")              # pop rdi
                    yield b("31 D2")           # xor edx, edx
                    yield b("85 C0")           # test eax, eax
                    yield b("0F 48 C2")        # cmovs eax, edx
                    yield b("88 07")           # mov byte ptr [rdi], al
            case Loop(body):
                # TODO: this only supports short jumps, that is, [-128..127]
                compiled_body = b"".join(_generate_body(body, linux_syscalls))

                # Displacements: 2 is the length in bytes of the jump to the
                # beginning, and 7 is the length of comparison and both jumps.
                distance = len(compiled_body)
                start_to_end = distance + 2
                end_to_start = 0x100 - distance - 7

                yield b("80 3F 00")           # cmp byte ptr [rdi], 0
                yield b("74", start_to_end)   # je end
                yield compiled_body
                yield b("EB", end_to_start)   # jmp start
