from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_x86_32_att(intermediate: AST) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield 'get_pc:'
    yield '    movl   (%esp), %ebx'
    yield '    ret'
    yield ''
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'
    yield '    pushl  %ebx'
    yield '    call   get_pc'
    yield '    addl   $_GLOBAL_OFFSET_TABLE_, %ebx'
    yield '    movl   8(%esp), %eax'



def _generate_body(intermediate: AST, parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(1):
                yield  '    incb   (%eax)'
            case Add(n):
                yield f'    addb   ${n}, (%eax)'
            case Subtract(1):
                yield  '    decb   (%eax)'
            case Subtract(n):
                yield f'    subb   ${n}, (%eax)'
            case Forward(1):
                yield  '    incl   %eax'
            case Forward(n):
                yield f'    addl   ${n}, %eax'
            case Back(1):
                yield  '    decl   %eax'
            case Back(n):
                yield f'    subl   ${n}, %eax'
            case Output(n):
                yield  '    pushl  %eax'
                yield  '    movzbl (%eax), %ecx'
                yield  '    pushl  %ecx'
                sequence = [
                       '    call   putchar@PLT',
                       '    movl   %eax, (%esp)'
                ] * n
                yield from sequence[:-1]
                yield  '    addl   $4, %esp'
                yield  '    popl   %eax'
            case Input(n):
                yield  '    pushl  %eax'
                yield  '    subl   $4, %esp'
                yield from ['    call getchar@PLT'] * n
                # EOF handling: replace negative values with 0.
                # Can't use cmovs because it requires i686.
                yield  '    xorl   %ecx, %ecx'
                yield  '    testl  %eax, %eax'
                yield  '    setns  %cl'
                yield  '    negl   %ecx'
                yield  '    andl   %eax, %ecx'
                yield  '    addl   $4, %esp'
                yield  '    popl   %eax'
                yield  '    movb   %cl, (%eax)'
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield  '    cmpb   $0, (%eax)'
                yield f'    je     end{label}'
                yield from _generate_body(body, label)
                yield f'    jmp    start{label}'
                yield f'end{label}:'
                loop_id += 1


def _generate_epilogue() -> Iterator[str]:
    yield '    popl   %ebx'
    yield '    ret'

