from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_x86_32_gas_intel(intermediate: AST) -> Iterator[str]:
    yield from _generate_prologue_gas()
    yield from _generate_body(intermediate, nasm=False)
    yield from _generate_epilogue()


def generate_x86_32_nasm(intermediate: AST) -> Iterator[str]:
    yield from _generate_prologue_nasm()
    yield from _generate_body(intermediate, nasm=True)
    yield from _generate_epilogue()


def _generate_prologue_gas() -> Iterator[str]:
    yield '    .intel_syntax noprefix'
    yield ''
    yield 'get_pc:'
    yield '    mov   ebx, dword ptr [esp]'
    yield '    ret'
    yield ''
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'
    yield '    push  ebx'
    yield '    call  get_pc'
    yield '    add   ebx, offset _GLOBAL_OFFSET_TABLE_'
    yield '    mov   eax, dword ptr [esp + 8]'


def _generate_prologue_nasm() -> Iterator[str]:
    yield '    extern getchar, putchar, _GLOBAL_OFFSET_TABLE_'
    yield '' 
    yield 'get_pc:'
    yield '    mov   ebx, dword [esp]'
    yield '    ret'
    yield ''
    yield '    global run'
    yield 'run:'
    yield '    push  ebx'
    yield '    call  get_pc'
    yield '    add   ebx, _GLOBAL_OFFSET_TABLE_ + $$ - $ wrt ..gotpc'
    yield '    mov   eax, dword [esp + 8]'


def _generate_epilogue() -> Iterator[str]:
    yield '    pop   ebx'
    yield '    ret'


def _generate_body(intermediate: AST, nasm: bool, parent_label: str='') -> Iterator[str]:
    if nasm:
        ptr = ""
        plt = " wrt ..plt" 
    else:
        ptr = " ptr"
        plt = "@PLT"
    loop_id = 0
    for node in intermediate:
        match node:
            case Add(1):
                yield f'    inc   byte{ptr} [eax]'
            case Add(n):
                yield f'    add   byte{ptr} [eax], {n}'
            case Subtract(1):
                yield f'    dec   byte{ptr} [eax]'
            case Subtract(n):
                yield f'    sub   byte{ptr} [eax], {n}'
            case Forward(1):
                yield  '    inc   eax'
            case Forward(n):
                yield f'    add   eax, {n}'
            case Back(1):
                yield  '    dec   eax'
            case Back(n):
                yield f'    sub   eax, {n}'
            case Output(n):
                yield  '    push  eax'
                yield f'    movzx ecx, byte{ptr} [eax]'
                yield  '    push  ecx'
                sequence = [
                      f'    call  putchar{plt}',
                      f'    mov   dword{ptr} [esp], eax'
                ] * n
                yield from sequence[:-1]
                yield  '    add   esp, 4'
                yield  '    pop   eax'
            case Input(n):
                yield  '    push  eax'
                yield  '    sub   esp, 4'
                yield from [f'    call  getchar{plt}'] * n
                # EOF handling: replace negative values with 0.
                # Can't use cmovs because it requires i686.
                yield  '    xor   ecx, ecx'
                yield  '    test  eax, eax'
                yield  '    setns cl'
                yield  '    neg   ecx'
                yield  '    and   ecx, eax'
                yield  '    add   esp, 4'
                yield  '    pop   eax'
                yield f'    mov   byte{ptr} [eax], cl'
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield f'    cmp   byte{ptr} [eax], 0'
                yield f'    je    end{label}'
                yield from _generate_body(body, nasm, label)
                yield f'    jmp   start{label}'
                yield f'end{label}:'
                loop_id += 1
