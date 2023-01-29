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
    yield 'get_pc:'
    yield '    mov   ebx, dword ptr [esp]'
    yield '    ret'
    yield ''
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'
    yield '    push  ebx'
    yield '    call  get_pc'
    yield '    add   ebx, offset _GLOBAL_OFFSET_TABLE_'
    yield '    mov   eax, dword ptr [esp + 8]'


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
                yield  '    push  eax'
                yield  '    push  dword ptr [eax]'
                sequence = [
                       '    call  putchar@PLT',
                       '    mov   dword ptr [esp], eax'
                ] * n
                yield from sequence[:-1]
                yield  '    pop   eax'
                yield  '    pop   eax'
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
    yield '    pop   ebx'
    yield '    ret'

