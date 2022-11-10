from typing import Iterator

from .intermediate import (
    Node, Loop,
    Increment, Decrement, MoveForward, MoveBack, Output, Input,
    Add, Subtract, MoveForwardBy, MoveBackBy, MultipleOutput, MultipleInput
)

def generate_x86_64_intel(intermediate: list[Node]) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '.globl run'
    yield '.intel_syntax noprefix'
    yield '.type run, @function'
    yield ''
    yield 'run:'


def _generate_body(intermediate: list[Node], parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Increment():      yield  '    inc   byte ptr [rdi]'
            case Decrement():      yield  '    dec   byte ptr [rdi]'
            case Add(n):           yield f'    add   byte ptr [rdi], {n}'
            case Subtract(n):      yield f'    sub   byte ptr [rdi], {n}'
            case MoveForward():    yield  '    inc   rdi'
            case MoveBack():       yield  '    dec   rdi'
            case MoveForwardBy(n): yield f'    add   rdi, {n}'
            case MoveBackBy(n):    yield f'    sub   rdi, {n}'
            case Output():
                yield '    push  rdi'
                yield '    movzx rdi, byte ptr [rdi]'
                yield '    call  putchar'
                yield '    pop   rdi'
            case Input():
                yield '    push  rdi'
                yield '    call  getchar'
                yield '    pop   rdi'
                yield '    mov   byte ptr [rdi], al'
            case MultipleOutput(count):
                yield '    push  rdi'
                yield '    movzx rdi, byte ptr [rdi]'
                sequence = ['    call  putchar', '    mov   rdi, rax'] * count
                yield from sequence[:-1]
                yield '    pop   rdi'
            case MultipleInput(count):
                yield '    push  rdi'
                yield from ['    call  getchar'] * count
                yield '    pop   rdi'
                yield '    mov   byte ptr [rdi], al'
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield  '    cmp   byte ptr [rdi], 0'
                yield f'    je    end{label}'
                yield from _generate_body(body, label)
                yield f'    jmp   start{label}'
                yield f'end{label}:'
                loop_id += 1


def _generate_epilogue() -> Iterator[str]:
    yield '    ret'
    yield ''
    yield '.section .note.GNU-stack, "", @progbits'
