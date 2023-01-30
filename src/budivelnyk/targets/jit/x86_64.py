from typing import Iterator

from ...intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

from .io import encoded_read_char, encoded_write_char


def generate_x86_64(intermediate: AST) -> bytes:
    return (b"".join(_generate_x86_64(intermediate)) + 
            b"\xc3") # ret # TODO: make it epilogue


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
            case Output(n): # TODO: wait, this is not!!!! n, this is 1
                yield b"\x57"                 # push rdi
                yield b"\x48\x0f\xb6\x3f"     # movzx rdi, byte ptr [rdi]
                yield b"\x48\xbe" + encoded_write_char # movabs rsi, encoded_write_char TODO actually I should move it to some register in the prologue, same with encoded_read_char, and restore them in the epilogue
                yield b"\xff\xd6"             # call rsi
                yield b"\x5f"                 # pop rdi
            case Input(n):
                pass # TODO
            case Loop(body):
                pass # TODO
