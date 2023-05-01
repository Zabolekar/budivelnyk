from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_x86_64_att(intermediate: AST) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'


def _generate_body(intermediate: AST, parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(1):
                yield  '    incb   (%rdi)'
            case Add(n):
                yield f'    addb   ${n}, (%rdi)'
            case Subtract(1):
                yield  '    decb   (%rdi)'
            case Subtract(n):
                yield f'    subb   ${n}, (%rdi)'
            case Forward(1):
                yield  '    incq   %rdi'
            case Forward(n):
                yield f'    addq   ${n}, %rdi'
            case Back(1):
                yield  '    decq   %rdi'
            case Back(n):
                yield f'    subq   ${n}, %rdi'
            case Output(n):
                yield '    pushq  %rdi'
                yield '    movzbq (%rdi), %rdi'
                sequence = ['    call   putchar', '    mov    %rax, %rdi'] * n
                yield from sequence[:-1]
                yield '    popq   %rdi'
            case Input(n):
                yield '    pushq  %rdi'
                yield from ['    call   getchar'] * n
                yield '    popq   %rdi'
                # EOF handling: replace negative values with 0.
                yield '    xorl   %edx, %edx'
                yield '    testl  %eax, %eax'
                yield '    cmovs  %edx, %eax'
                yield '    movb   %al, (%rdi)'
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield  '    cmpb   $0, (%rdi)'
                yield f'    je     end{label}'
                yield from _generate_body(body, label)
                yield f'    jmp    start{label}'
                yield f'end{label}:'
                loop_id += 1


def _generate_epilogue() -> Iterator[str]:
    yield '    ret'
    yield ''
    yield '#ifdef LINUX'
    yield '    .section .note.GNU-stack, "", @progbits'
    yield '#endif'

