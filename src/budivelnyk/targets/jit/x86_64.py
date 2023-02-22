from typing import Iterator

from ...intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

from .io import encoded_read_char, encoded_write_char


def generate_x86_64(intermediate: AST) -> bytes:
    return (_generate_prologue()
          + b"".join(_generate_body(intermediate))
          + _generate_epilogue())


def _generate_prologue() -> bytes:
    return (b"\x41\x54"                       # push r12
          + b"\x41\x55"                       # push r13
          + b"\x49\xbc" + encoded_write_char  # movabs r12, encoded_write_char
          + b"\x49\xbd" + encoded_read_char)  # movabs r13, encoded_read_char


def _generate_body(intermediate: AST) -> Iterator[bytes]:
    for node in intermediate:
        match node:
            case Add(1):
                yield b"\xfe\x07"  # inc byte ptr [rdi]
            case Add(n):
                yield b"\x80\x07" + bytes([n])  # add byte ptr [rdi], n
            case Subtract(1):
                yield b"\xfe\x0f"  # dec byte ptr [rdi]
            case Subtract(n):
                yield b"\x80\x2f" + bytes([n])  # sub byte ptr [rdi], n
            case Forward(1):
                yield b"\x48\xff\xc7"  # inc rdi
            case Forward(n):
                yield b"\x48\x83\xc7" + bytes([n])  # add rdi, n
            case Back(1):
                yield b"\x48\xff\xcf"  # dec rdi
            case Back(n):
                yield b"\x48\x83\xef" + bytes([n])  # sub rdi, n
            case Output(n):
                yield b"\x57"               # push rdi
                yield b"\x48\x0f\xb6\x3f"   # movzx rdi, byte ptr [rdi]
                sequence = [
                    b"\x41\xff\xd4",        # call r12 (see prologue)
                    b"\x48\x89\xc7"         # mov rdi, rax
                ] * n
                yield from sequence[:-1]
                yield b"\x5f"               # pop rdi
            case Input(n):
                yield b"\x57"               # push   rdi
                yield from [
                    b"\x41\xff\xd5"         # call r13 (see prologue)
                ] * n
                yield b"\x5f"               # pop rdi
                yield b"\x31\xd2"           # xor edx, edx
                yield b"\x85\xc0"           # test eax, eax
                yield b"\x0f\x48\xc2"       # cmovs eax, edx
                yield b"\x88\x07"           # mov byte ptr [rdi], al
            case Loop(body):
                # TODO: this only supports short jumps, that is, [-128..127]
                compiled_body = b"".join(_generate_body(body))

                # Displacements: 2 is the length in bytes of the jump to the
                # beginning, and 7 is the length of comparison and both jumps.
                distance = len(compiled_body)
                start_to_end = distance + 2
                end_to_start = 0x100 - distance - 7

                yield b"\x80\x3f\x00"                  # cmp byte ptr [rdi], 0
                yield b"\x74" + bytes([start_to_end])  # je end
                yield compiled_body
                yield b"\xeb" + bytes([end_to_start])  # jmp start


def _generate_epilogue() -> bytes:
    return (b"\x41\x5d"  # pop r13
          + b"\x41\x5c"  # pop r12
          + b"\xc3")     # ret
