from typing import Iterator

from .intermediate import (
    Node, Loop,
    Increment, Decrement, MoveForward, MoveBack, Output, Input,
    Add, Subtract, MoveForwardBy, MoveBackBy, MultipleOutput, MultipleInput
)

def generate_x86_64_att(intermediate: list[Node]) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '.globl run'
    yield '.type run, @function'
    yield ''
    yield 'run:'


def _generate_body(intermediate: list[Node], parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Increment():      yield  '    incb   (%rdi)'
            case Decrement():      yield  '    decb   (%rdi)'
            case Add(n):           yield f'    addb   ${n}, (%rdi)'
            case Subtract(n):      yield f'    subb   ${n}, (%rdi)'
            case MoveForward():    yield  '    incq   %rdi'
            case MoveBack():       yield  '    decq   %rdi'
            case MoveForwardBy(n): yield f'    addq   ${n}, %rdi'
            case MoveBackBy(n):    yield f'    subq   ${n}, %rdi'
            case Output():
                yield '    pushq  %rdi'
                yield '    movzbq (%rdi), %rdi'
                yield '    call   putchar'
                yield '    popq   %rdi'
            case Input():
                yield '    pushq  %rdi'
                yield '    call   getchar'
                yield '    popq   %rdi'
                yield '    movb   %al, (%rdi)'
            case MultipleOutput(count):
                yield '    pushq  %rdi'
                yield '    movzbq (%rdi), %rdi'
                sequence = ['    call   putchar', '    mov    %rax, %rdi'] * count
                yield from sequence[:-1]
                yield '    popq   %rdi'
            case MultipleInput(count):
                yield '    pushq  %rdi'
                yield from ['    call   getchar'] * count
                yield '    popq   %rdi'
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
    yield '.section .note.GNU-stack, "", @progbits'
