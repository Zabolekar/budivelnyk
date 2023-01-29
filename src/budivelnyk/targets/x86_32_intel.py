from typing import Iterator
from platform import system

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_x86_32_intel(intermediate: AST) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '    .intel_syntax noprefix'
    yield ''
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'
    yield '    mov   eax, [esp + 4]'


def _generate_body(intermediate: AST, parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(1):
                yield  '    inc   byte ptr [eax]'
            case Add(n):
                yield f'    add   byte ptr [eax], {n}'
            case Subtract(1):
                yield  '    dec   byte ptr [eax]'
            case Subtract(n):
                yield f'    sub   byte ptr [eax], {n}'
            case Forward(1):
                yield  '    inc   eax'
            case Forward(n):
                yield f'    add   eax, {n}'
            case Back(1):
                yield  '    dec   eax'
            case Back(n):
                yield f'    sub   eax, {n}'
            case Output(n):
                raise NotImplementedError
            case Input(n):
                raise NotImplementedError
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield  '    cmp   byte ptr [eax], 0'
                yield f'    je    end{label}'
                yield from _generate_body(body, label)
                yield f'    jmp   start{label}'
                yield f'end{label}:'
                loop_id += 1


def _generate_epilogue() -> Iterator[str]:
    yield '    ret'

