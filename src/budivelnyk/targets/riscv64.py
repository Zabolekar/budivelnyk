from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_riscv64(intermediate: AST) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '    .align 1'
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'
    yield '    addi   sp, sp, -16'
    yield '    sd     ra, 8(sp)'
    yield '    sd     s0, 0(sp)'

def _generate_body(intermediate: AST, parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(n):
                yield  '    lb     a1, 0(a0)'
                yield f'    addi   a1, a1, {n}'
                yield  '    sb     a1, 0(a0)'
            case Subtract(n):
                yield  '    lb     a1, 0(a0)'
                yield f'    addi   a1, a1, -{n}'
                yield  '    sb     a1, 0(a0)'
            case Forward(n):
                yield f'    addi   a0, a0, {n}'
            case Back(n):
                yield f'    addi   a0, a0, -{n}'
            case Output(n):
                yield  '    mv     s0, a0'
                yield  '    lb     a0, 0(a0)'
                yield from ['    call   putchar'] * n
                yield  '    mv     a0, s0'
            case Input(n):
                yield  '    mv     s0, a0'
                yield from ['    call   getchar'] * n
                # a0 := a0 if a0 > 0 else 0: 
                yield  '    sgtz   a1, a0'
                yield  '    neg    a1, a1'
                yield  '    and    a0, a0, a1'
                yield  '    sb     a0, 0(s0)'
                yield  '    mv     a0, s0'
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield  '    lb     a1, 0(a0)'
                yield f'    beq    a1, zero, end{label}'
                yield from _generate_body(body, label)
                yield f'    j      start{label}'
                yield f'end{label}:'
                loop_id += 1


def _generate_epilogue() -> Iterator[str]:
    yield '    ld     s0, 0(sp)'
    yield '    ld     ra, 8(sp)'
    yield '    addi   sp, sp, 16'
    yield '    ret'
    yield '    .section .note.GNU-stack,"",@progbits'

