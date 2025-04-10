from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_arm32(intermediate: AST, *, thumb: bool) -> Iterator[str]:
    yield from _generate_prologue(thumb=thumb)
    yield from _generate_body(intermediate, thumb=thumb)
    yield from _generate_epilogue()


def _generate_prologue(*, thumb: bool) -> Iterator[str]:
    yield '    .arch armv7-a'
    if thumb:
        yield '    .thumb'
    else:
        yield '    .arm'
    yield '    .syntax unified'
    yield ''
    yield '    .align 1'
    yield '    .globl run'
    yield '    .type run, %function'
    yield 'run:'
    yield  '    push   {r4, lr}'  # r4 is the first callee-saved register


def _generate_epilogue() -> Iterator[str]:
    yield  '    pop    {r4, pc}'


def _generate_body(intermediate: AST, parent_label: str='', *, thumb: bool) -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(n):
                yield  '    ldrb   r1, [r0]'
                yield f'    add    r1, r1, {n}'
                yield  '    strb   r1, [r0]'
            case Subtract(n):
                yield  '    ldrb   r1, [r0]'
                yield f'    sub    r1, r1, {n}'
                yield  '    strb   r1, [r0]'
            case Forward(n):
                yield f'    add    r0, r0, {n}'
            case Back(n):
                yield f'    sub    r0, r0, {n}'
            case Output(n):
                yield  '    mov    r4, r0'
                yield  '    ldrb   r0, [r0]'
                yield from ['    bl     putchar'] * n
                yield  '    mov    r0, r4'
            case Input(n):
                yield  '    mov    r4, r0'
                yield from ['    bl     getchar'] * n
                # EOF handling: replace negative values with 0.
                yield  '    cmp    r0, 0'
                yield  '    ite    ge'
                yield  '    movge  r1, r0'
                yield  '    movlt  r1, 0'
                yield  '    mov    r0, r4'
                yield  '    strb   r1, [r0]'

            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield  '    ldrb   r1, [r0]'
                if thumb:
                    yield f'    cbz    r1, end{label}'
                else:
                    yield  '    cmp    r1, 0'
                    yield f'    beq    end{label}'
                yield from _generate_body(body, label, thumb=thumb)
                yield f'    b      start{label}'
                yield f'end{label}:'
                loop_id += 1
