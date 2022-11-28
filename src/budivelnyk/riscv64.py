from typing import Iterator

from .intermediate import (
    Node, Loop,
    Increment, Decrement, MoveForward, MoveBack, Output, Input,
    Add, Subtract, MoveForwardBy, MoveBackBy, MultipleOutput, MultipleInput
)

def generate_riscv64(intermediate: list[Node]) -> Iterator[str]:
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

def _generate_body(intermediate: list[Node], parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Increment():
                yield  '    lb     a1, 0(a0)'
                yield  '    addi   a1, a1, 1'
                yield  '    sb     a1, 0(a0)'
            case Decrement():
                yield  '    lb     a1, 0(a0)'
                yield  '    addi   a1, a1, -1'
                yield  '    sb     a1, 0(a0)'
            case Add(n):
                yield  '    lb     a1, 0(a0)'
                yield f'    addi   a1, a1, {n}'
                yield  '    sb     a1, 0(a0)'
            case Subtract(n):
                yield  '    lb     a1, 0(a0)'
                yield f'    addi   a1, a1, -{n}'
                yield  '    sb     a1, 0(a0)'
            case MoveForward():
                yield  '    addi   a0, a0, 1'
            case MoveBack():
                yield  '    addi   a0, a0, -1'
            case MoveForwardBy(n):
                yield f'    addi   a0, a0, {n}'
            case MoveBackBy(n):
                yield f'    addi   a0, a0, -{n}'
            case Output():
                yield  '    mv     s0, a0'
                yield  '    lb     a0, 0(a0)'
                yield  '    call   putchar'
                yield  '    mv     a0, s0'
            case Input():
                yield  '    mv     s0, a0'
                yield  '    call   getchar'
                yield  '    sgtz   a1, a0'
                yield  '    neg    a1, a1'
                yield  '    and    a0, a0, a1'
                yield  '    sb     a0, 0(s0)'
                yield  '    mv     a0, s0'
            case MultipleOutput(count):
                yield  '    mv     s0, a0'
                yield  '    lb     a0, 0(a0)'
                yield from ['    call   putchar'] * count
                yield  '    mv     a0, s0'
            case MultipleInput(count):
                yield  '    mv     s0, a0'
                yield from ['    call   getchar'] * count
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

