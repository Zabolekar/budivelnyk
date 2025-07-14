from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_ppc32(intermediate: AST) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '    .machine ppc7400'
    yield '    .align 2'
    yield '    .globl _run'  # note the _, it's a Mac OS X peculiarity
    yield '_run:'
    # I'm not sure why the stack has to be like this, but this is how GCC 4.0
    # does it. See also (but it's for AIX, not for Mac OS X!):
    # https://www.ibm.com/docs/en/aix/7.1?topic=overview-prologs-epilogs
    yield '    mflr   r0'
    yield '    stw    r0, 8(r1)'
    yield '    stw    r30, -8(r1)'
    yield '    stwu   r1, -80(r1)'


def _generate_epilogue() -> Iterator[str]:
    yield '    addi   r1, r1, 80'
    yield '    lwz    r30, -8(r1)'
    yield '    lwz    r0, 8(r1)'
    yield '    mtlr   r0'
    yield '    blr'


def _generate_body(intermediate: AST, parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(n):
                yield  '    lbz    r4, 0(r3)'
                yield f'    addi   r4, r4, {n}'
                yield  '    stb    r4, 0(r3)'
            case Subtract(n):
                yield  '    lbz    r4, 0(r3)'
                yield f'    subi   r4, r4, {n}'
                yield  '    stb    r4, 0(r3)'
            case Forward(n):
                yield f'    addi   r3, r3, {n}'
            case Back(n):
                yield f'    subi   r3, r3, {n}'
            case Output(n):
                yield  '    mr     r30, r3'
                yield  '    lbz    r3, 0(r3)'
                yield from ['    bl     _putchar'] * n
                yield  '    mr     r3, r30'
            case Input(n):
                yield  '    mr     r30, r3'
                yield from ['    bl     _getchar'] * n
                # TODO: test multiple input sequences with multiple EOFs
                # EOF handling: replace negative values with 0.
                yield  '    cmpwi  r3, 0'
                yield  '    bge+   1f'
                yield  '    li     r3, 0'
                yield  '1:  stb    r3, 0(r30)'
                yield  '    mr     r3, r30'
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield  '    lbz    r4, 0(r3)'
                yield  '    cmplwi r4, 0'
                yield f'    beq-   end{label}'
                yield from _generate_body(body, label)
                yield f'    b      start{label}'
                yield f'end{label}:'
                loop_id += 1
