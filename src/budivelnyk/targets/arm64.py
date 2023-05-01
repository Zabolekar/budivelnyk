from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_arm64(intermediate: AST) -> Iterator[str]:
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
    yield '    stp    x29, x30, [sp, -32]!'
    yield '    mov    x29, sp'
    yield '    str    x19, [sp, 16]'  # x19 is the first callee-saved register

def _generate_body(intermediate: AST, parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(n):
                yield  '    ldrb   w1, [x0]'
                yield f'    add    w1, w1, {n}'
                yield  '    strb   w1, [x0]'
            case Subtract(n):
                yield  '    ldrb   w1, [x0]'
                yield f'    sub    w1, w1, {n}'
                yield  '    strb   w1, [x0]'
            case Forward(n):
                yield f'    add    x0, x0, {n}'
            case Back(n):
                yield f'    sub    x0, x0, {n}'
            case Output(n):
                yield  '    mov    x19, x0'
                yield  '    ldrb   w0, [x0]'
                yield from ['    bl     putchar'] * n
                yield  '    mov    x0, x19'
            case Input(n):
                yield  '    mov    x19, x0'
                yield from ['    bl     getchar'] * n
                # EOF handling: replace negative values with 0.
                yield  '    cmp    w0, 0'
                yield  '    csel   w1, w0, wzr, ge'
                yield  '    mov    x0, x19'
                yield  '    strb   w1, [x0]'
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
    yield '    ldr    x19, [sp, 16]'
    yield '    ldp    x29, x30, [sp], 32'
    yield '    ret'

