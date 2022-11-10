from typing import Iterator

from .intermediate import (
    Node, Cycle,
    Increment, Decrement, MoveForward, MoveBack, Output, Input,
    AddConstant, MoveByConstant
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
    cycle_id = 0
    for node in intermediate:
        match node:
            case Increment():       yield  '    inc   byte ptr [rdi]'
            case Decrement():       yield  '    dec   byte ptr [rdi]'
            case AddConstant(n):    yield f'    add   byte ptr [rdi], {n}'
            case MoveForward():     yield  '    inc   rdi'
            case MoveBack():        yield  '    dec   rdi'
            case MoveByConstant(n): yield f'    add   rdi, {n}'
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
            case Cycle(body):
                label = f'{parent_label}_{cycle_id}'
                yield f'start{label}:'
                yield  '    cmp   byte ptr [rdi], 0'
                yield f'    je    end{label}'
                yield from _generate_body(body, label)
                yield f'    jmp   start{label}'
                yield f'end{label}:'
                cycle_id += 1


def _generate_epilogue() -> Iterator[str]:
    yield '    ret'
    yield ''
    yield '.section .note.GNU-stack, "", @progbits'
