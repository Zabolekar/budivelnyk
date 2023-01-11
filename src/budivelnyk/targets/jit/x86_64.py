from typing import Iterator

from ...intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)


def generate_x86_64(intermediate: AST) -> bytes:
    return (b"".join(_generate_x86_64(intermediate)) + 
            b"\xc3") # ret


def _generate_x86_64(intermediate: AST) -> Iterator[bytes]:
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
                pass # TODO
            case Input(n):
                pass # TODO
            case Loop(body):
                pass # TODO
