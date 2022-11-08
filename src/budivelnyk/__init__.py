"""
Compile bf to asm. Cell size is one byte.
"""

import subprocess
from platform import machine


def fill_jump_tables(intermediate: list[str]) -> dict[int, int]:
    jumps = {}
    stack = []
    for i, command in enumerate(intermediate):
        if command == '[':
            stack.append(i)
        elif command == ']':
            j = stack.pop()
            jumps[j] = i
            jumps[i] = j
    return jumps

def bf_to_intermediate(bf_code: str) -> list[str]:
    """
    Currently all it does is grouping consecutive identical
    + - < > , . commands together and stripping comments.
    """
    
    result: list[str] = []

    group = False
    allowed = "+-><[].,"
    groupable = "+-><.,"

    for command in bf_code:
        if command not in allowed:
            continue
        if command in groupable:
            if len(result) > 0:
                if result[-1].endswith(command):
                    result[-1] += command
                    continue
        result.append(command)

    return result

def generate_x86_64(intermediate: list[str]):
    jumps = fill_jump_tables(intermediate)

    yield ".globl run"
    yield ".type run, @function"
    yield "run:"

    for i, command in enumerate(intermediate):
        n = len(command)

        if command.startswith("+"):
            if n == 1:
                yield "incb (%rdi)"
            else:
                yield f"addb ${n}, (%rdi)"
        elif command.startswith("-"):
            if n == 1:
                yield "decb (%rdi)"
            else:
                yield f"subb ${n}, (%rdi)"
        elif command.startswith(">"):
            if n == 1:
                yield "incq %rdi"
            else:
                yield f"addq ${n}, %rdi"
        elif command.startswith("<"):
            if n == 1:
                yield "decq %rdi"
            else:
                yield f"subq ${n}, %rdi"
        elif command == '[':
            suffix = f"{i}_{jumps[i]}"
            yield f"start_{suffix}:"
            yield "cmpb $0, (%rdi)"
            yield f"je end_{suffix}"
        elif command == ']':
            suffix = f"{jumps[i]}_{i}"
            yield f"jmp start_{suffix}"
            yield f"end_{suffix}:"
        elif command.startswith("."):
            yield "pushq %rdi"
            yield "movq (%rdi), %rdi"
            sequence = ["call putchar", "mov %rax, %rdi"] * n
            yield from sequence[:-1]
            yield "popq %rdi"
        elif command.startswith(","):
            yield "pushq %rdi"
            yield from ["call getchar"] * n
            yield "popq %rdi"
            yield "movb %al, (%rdi)"
    yield "ret"
    yield '.section .note.GNU-stack,"",@progbits'


def bf_to_asm(input_path: str, output_path: str):
    with open(input_path) as input_file:
        bf_code = input_file.read()

    intermediate = bf_to_intermediate(bf_code)

    with open(output_path, 'w') as output_file:
        if machine() == "x86_64":
            lines = generate_x86_64(intermediate)
            print(*lines, sep="\n", file=output_file)
        else:
            raise RuntimeError("unknown architecture")


def bf_to_shared(input_path: str, asm_path: str, output_path: str):
    bf_to_asm(input_path, asm_path)
    asm_to_shared = ["cc", "-shared", "-o", output_path, asm_path]
    subprocess.run(asm_to_shared).check_returncode()
