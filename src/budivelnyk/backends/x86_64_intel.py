from __future__ import annotations
from typing import Iterator, TYPE_CHECKING
from .enums import Format, InputOutput
from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)
if TYPE_CHECKING:
    from . import Backend


def generate_x86_64_gas_intel(intermediate: AST, backend: Backend) -> Iterator[str]:
    yield from _generate_prologue_gas(backend)
    yield from _generate_body(intermediate, backend, nasm=False)
    yield from _generate_epilogue()


def generate_x86_64_nasm(intermediate: AST, backend: Backend) -> Iterator[str]:
    yield from _generate_prologue_nasm(backend)
    yield from _generate_body(intermediate, backend, nasm=True)
    yield from _generate_epilogue()


def _generate_prologue_gas(backend: Backend) -> Iterator[str]:
    yield '    .intel_syntax noprefix'
    yield ''
    match backend.format:
        case Format.MACHO:
            yield '    .globl _run'
            yield '_run:'
        case Format.ELF:
            yield '    .globl run'
            yield '    .type run, @function'
            yield 'run:'


def _generate_prologue_nasm(backend: Backend) -> Iterator[str]:
    match backend.format:
        case Format.MACHO:
            yield f'    extern _getchar, _putchar'  # TODO: eliminate if IO not used, check if needed at all
            yield '    global _run'
            yield '_run:'
        case Format.ELF:
            if backend.io == InputOutput.LIBC:
                yield f'    extern getchar, putchar'  # TODO: eliminate if IO not used, explain why not needed for i486
            yield '    global run:function'
            yield 'run:'


def _generate_epilogue() -> Iterator[str]:
    yield '    mov   rax, rdi'
    yield '    ret'


def _generate_body(intermediate: AST, backend: Backend, nasm: bool, parent_label: str='') -> Iterator[str]:
    match backend.format:
        case Format.MACHO:
            putchar, getchar = "_putchar", "_getchar"
        case Format.ELF:
            putchar, getchar = "putchar", "getchar"

    linux_syscalls: bool = backend.io == InputOutput.LINUX_SYSCALLS

    if nasm:
        ptr = ""
        plt = " wrt ..plt" if backend.format == Format.ELF else ""
    else:
        ptr = " ptr"
        plt = "@plt" if backend.format == Format.ELF else ""  # "" should work everywhere, TODO: understand/document

    loop_id = 0
    input_id = 0
    for node in intermediate:
        match node:
            case Add(1):
                yield f'    inc   byte{ptr} [rdi]'
            case Add(n):
                yield f'    add   byte{ptr} [rdi], {n}'
            case Subtract(1):
                yield f'    dec   byte{ptr} [rdi]'
            case Subtract(n):
                yield f'    sub   byte{ptr} [rdi], {n}'
            case Forward(1):
                yield  '    inc   rdi'
            case Forward(n):
                yield f'    add   rdi, {n}'
            case Back(1):
                yield  '    dec   rdi'
            case Back(n):
                yield f'    sub   rdi, {n}'
            case Output(n):
                if linux_syscalls:
                    yield '    mov   rsi, rdi'
                    yield '    mov   edi, 1'  # stdout
                    yield '    mov   edx, 1'  # length
                    sequence = [
                        '    mov   eax, 1',  # write
                        '    syscall'
                    ] * n
                    yield from sequence
                    yield '    mov   rdi, rsi'
                else:
                    yield  '    push  rdi'
                    yield f'    movzx rdi, byte{ptr} [rdi]'
                    sequence = [f'    call  {putchar}{plt}', '    mov   rdi, rax'] * n
                    yield from sequence[:-1]
                    yield  '    pop   rdi'
            case Input(n):
                if linux_syscalls:
                    yield '    mov   rsi, rdi'
                    yield '    mov   edi, 0'  # stdin
                    yield '    mov   edx, 1'  # length
                    sequence = [
                        '    mov   eax, 0',  # read
                        '    syscall'
                    ] * n
                    yield from sequence
                    yield '    mov   rdi, rsi'
                    # EOF handling: unless read returns 1 (1 byte read), write 0 to tape.
                    label = f"read_{input_id}_done"
                    yield  '    cmp   eax, 1'
                    yield f'    je    {label}'
                    yield f'    mov   byte{ptr} [rdi], 0'
                    yield f'{label}:'
                    input_id += 1
                else:
                    yield  '    push  rdi'
                    yield from [f'    call  {getchar}{plt}'] * n
                    yield  '    pop   rdi'
                    # EOF handling: replace negative values with 0.
                    yield  '    xor   edx, edx'
                    yield  '    test  eax, eax'
                    yield  '    cmovs eax, edx'
                    yield f'    mov   byte{ptr} [rdi], al'
            case Loop(body):
                label = f'{parent_label}_{loop_id}'
                yield f'start{label}:'
                yield f'    cmp   byte{ptr} [rdi], 0'
                yield f'    je    end{label}'
                yield from _generate_body(body, backend, nasm, label)
                yield f'    jmp   start{label}'
                yield f'end{label}:'
                loop_id += 1
