from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_x86_64_intel(intermediate: AST) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '    .intel_syntax noprefix'
    yield ''
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'


def _generate_body(intermediate: AST, parent_label: str='') -> Iterator[str]:
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(1):
                yield  '    inc   byte ptr [rdi]'
            case Add(n):
                yield f'    add   byte ptr [rdi], {n}'
            case Subtract(1):
                yield  '    dec   byte ptr [rdi]'
            case Subtract(n):
                yield f'    sub   byte ptr [rdi], {n}'
            case Forward(1):
                yield  '    inc   rdi'
            case Forward(n):
                yield f'    add   rdi, {n}'
            case Back(1):
                yield  '    dec   rdi'
            case Back(n):
                yield f'    sub   rdi, {n}'
            case Output(n):
                yield '    push  rdi'
                yield '    movzx rdi, byte ptr [rdi]'
                sequence = ['    call  putchar', '    mov   rdi, rax'] * n
                yield from sequence[:-1]
                yield '    pop   rdi'
            case Input(n):
                yield '    push  rdi'
                yield from ['    call  getchar'] * n
                yield '    pop   rdi'
                # EOF handling: replace -1 with 0
                yield '    xor   edx, edx'
                yield '    test  eax, eax'
                yield '    cmovs eax, edx'
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
    yield '#ifdef LINUX'
    yield '    .section .note.GNU-stack, "", @progbits'
    yield '#endif'

