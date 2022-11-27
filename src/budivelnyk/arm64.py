from typing import Iterator

from .intermediate import (
    Node, Loop,
    Increment, Decrement, MoveForward, MoveBack, Output, Input,
    Add, Subtract, MoveForwardBy, MoveBackBy, MultipleOutput, MultipleInput
)

def generate_arm64(intermediate: list[Node]) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '    .arch armv8-a'
    yield ''
    yield '    .align 2'
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'


def _generate_body(intermediate: list[Node], parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Increment():
                yield  '    ldrb   w1, [x0]'
                yield  '    add    w1, w1, 1'
                yield  '    strb   w1, [x0]'
            case Decrement():
                yield  '    ldrb   w1, [x0]'
                yield  '    sub    w1, w1, 1'
                yield  '    strb   w1, [x0]'
            case Add(n):
                yield  '    ldrb   w1, [x0]'
                yield f'    add    w1, w1, {n}'
                yield  '    strb   w1, [x0]'
            case Subtract(n):
                yield  '    ldrb   w1, [x0]'
                yield f'    sub    w1, w1, {n}'
                yield  '    strb   w1, [x0]'
            case MoveForward():
                yield  '    add    x0, x0, 1'
            case MoveBack():
                yield  '    sub    x0, x0, 1'
            case MoveForwardBy(n):
                yield f'    add    x0, x0, {n}'
            case MoveBackBy(n):
                yield f'    sub    x0, x0, {n}'
            case Output():
                yield  '    stp    x29, x30, [sp, -32]!'
                yield  '    mov    x29, sp'
                yield  '    str    x0, [sp, 16]'
                yield  '    ldrb   w0, [x0]'
                yield  '    bl     putchar'
                yield  '    ldr    x0, [sp, 16]'
                yield  '    ldp    x29, x30, [sp], 32'
            case Input():
                yield  '    stp    x29, x30, [sp, -32]!'
                yield  '    mov    x29, sp'
                yield  '    str    x0, [sp, 16]'
                yield  '    bl     getchar'
                yield  '    mov    w1, w0'
                yield  '    ldr    x0, [sp, 16]'
                yield  '    strb   w1, [x0]'
                yield  '    ldp    x29, x30, [sp], 32'
            case MultipleOutput(count):
                yield  '    stp    x29, x30, [sp, -32]!'
                yield  '    mov    x29, sp'
                yield  '    str    x0, [sp, 16]'
                yield  '    ldrb   w0, [x0]'
                yield from ['    bl     putchar'] * count
                yield  '    ldr    x0, [sp, 16]'
                yield  '    ldp    x29, x30, [sp], 32'
            case MultipleInput(count):
                yield  '    stp    x29, x30, [sp, -32]!'
                yield  '    mov    x29, sp'
                yield  '    str    x0, [sp, 16]'
                yield from ['    bl     getchar'] * count
                yield  '    mov    w1, w0'
                yield  '    ldr    x0, [sp, 16]'
                yield  '    strb   w1, [x0]'
                yield  '    ldp    x29, x30, [sp], 32'
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield  '    ldrb   w1, [x0]'
                yield f'    cbz    w1, end{label}'
                yield from _generate_body(body, label)
                yield f'    b      start{label}'
                yield f'end{label}:'
                loop_id += 1


def _generate_epilogue() -> Iterator[str]:
    yield '    ret'

