from typing import Iterator

from ..intermediate import (
    AST, Loop,
    Add, Subtract, Forward, Back, Output, Input
)

def generate_x86_64_att(intermediate: AST, *, linux_syscalls: bool) -> Iterator[str]:
    yield from _generate_prologue()
    yield from _generate_body(intermediate, linux_syscalls)
    yield from _generate_epilogue()


def _generate_prologue() -> Iterator[str]:
    yield '    .globl run'
    yield '    .type run, @function'
    yield 'run:'


def _generate_epilogue() -> Iterator[str]:
    yield '    ret'
    yield ''
    yield '#ifdef LINUX'
    yield '    .section .note.GNU-stack, "", @progbits'
    yield '#endif'


def _generate_body(intermediate: AST, linux_syscalls: bool, parent_label: str='') -> Iterator[str]:
    loop_id = 0
    input_id = 0
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
                if linux_syscalls:
                    yield '    movq   %rdi, %rsi'
                    yield '    movl   $1, %edi'  # stdout
                    yield '    movl   $1, %edx'  # length
                    sequence = [
                        '    movl   $1, %eax',  # write
                        '    syscall'
                    ] * n
                    yield from sequence
                    yield '    movq   %rsi, %rdi'
                else:
                    yield '    pushq  %rdi'
                    yield '    movzbq (%rdi), %rdi'
                    sequence = ['    call   putchar', '    mov    %rax, %rdi'] * n
                    yield from sequence[:-1]
                    yield '    popq   %rdi'
            case Input(n):
                if linux_syscalls:
                    yield '    movq   %rdi, %rsi'
                    yield '    movl   $0, %edi'  # stdin
                    yield '    movl   $1, %edx'  # length
                    sequence = [
                        '    movl   $0, %eax',  # read
                        '    syscall'
                    ] * n
                    yield from sequence
                    yield '    movq   %rsi, %rdi'
                    # EOF handling: unless read returns 1 (1 byte read), write 0 to tape.
                    label = f"read_{input_id}_done"
                    yield  '    cmpl   $1, %eax'
                    yield f'    je     {label}'
                    yield f'    movb   $0, (%rdi)'
                    yield f'{label}:'
                    input_id += 1
                else:
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
                yield from _generate_body(body, linux_syscalls, label)
                yield f'    jmp    start{label}'
                yield f'end{label}:'
                loop_id += 1
