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
                yield b"\xfe\x07"
            case Add(n):
                yield b"\x80\x07" + bytes([n])
            case Subtract(1):
                pass # TODO
            case Subtract(n):
                pass # TODO
            case Forward(1):
                yield b"\x48\xff\xc7"
            case Forward(n):
                pass # TODO
            case Back(1):
                pass # TODO
            case Back(n):
                pass # TODO
            case Output(n):
                pass # TODO
            case Input(n):
                pass # TODO
            case Loop(body):
                pass # TODO
