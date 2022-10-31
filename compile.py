"""
Compile bf to asm. Cell size is one byte.
"""

from sys import argv
from platform import machine

def fill_jump_tables(bf_code: str) -> tuple[dict[int, int], dict[int, int]]:
    forward_jumps = {}
    backward_jumps = {}
    stack = []
    for i, c in enumerate(bf_code):
        if c == '[':
            stack.append(i)
        elif c == ']':
            j = stack.pop()
            forward_jumps[j] = i
            backward_jumps[i] = j
    return forward_jumps, backward_jumps

def compile_to_x86_64(bf_code):
    yield ".globl run"
    yield ".type run, @function"
    yield "run:"
    for i, c in enumerate(bf_code):
        if c == '+':
            yield "incb (%rdi)"
        elif c == '-':
            yield "decb (%rdi)"
        elif c == '>':
            yield "incq %rdi"
        elif c == '<':
            yield "decq %rdi"
        elif c == '[':
            suffix = f"{i}_{forward_jumps[i]}"
            yield f"start_{suffix}:"
            yield "cmpb $0, (%rdi)"
            yield f"je end_{suffix}"
        elif c == ']':
            suffix = f"{backward_jumps[i]}_{i}"
            yield f"jmp start_{suffix}"
            yield f"end_{suffix}:"
        elif c == ".":
            yield "pushq %rdi"
            yield "movq (%rdi), %rdi"
            yield "call putchar"
            yield "popq %rdi"
        elif c == ",":
            yield "pushq %rdi"
            yield "call getchar"
            yield "popq %rdi"
            yield "movb %al, (%rdi)"
    yield "ret"
    yield '.section .note.GNU-stack,"",@progbits'

if __name__ == "__main__":
    input_path, output_path = argv[1:]
    with open(input_path) as input_file:
        bf_code = input_file.read()

    forward_jumps, backward_jumps = fill_jump_tables(bf_code)

    with open(output_path, 'w') as output_file:
        if machine() == "x86_64":
            lines = compile_to_x86_64(bf_code)
            print(*lines, sep="\n", file=output_file)
        else:
            raise RuntimeError("unknown architecture")
