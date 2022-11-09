"""
Compile bf to asm. Cell size is one byte.
"""

from __future__ import annotations
import enum
import subprocess
from typing import Iterator
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


def generate_x86_64_att(intermediate: list[str]) -> Iterator[str]:
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
            yield "movzbq (%rdi), %rdi"
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


def generate_x86_64_intel(intermediate: list[str]) -> Iterator[str]:
    jumps = fill_jump_tables(intermediate)

    yield ".globl run"
    yield ".intel_syntax noprefix"
    yield ".type run, @function"
    yield "run:"

    for i, command in enumerate(intermediate):
        n = len(command)

        if command.startswith("+"):
            if n == 1:
                yield "inc byte ptr [rdi]"
            else:
                yield f"add byte ptr [rdi], {n}"
        elif command.startswith("-"):
            if n == 1:
                yield "dec byte ptr [rdi]"
            else:
                yield f"sub byte ptr [rdi], {n}"
        elif command.startswith(">"):
            if n == 1:
                yield "inc rdi"
            else:
                yield f"add rdi, {n}"
        elif command.startswith("<"):
            if n == 1:
                yield "dec rdi"
            else:
                yield f"sub rdi, {n}"
        elif command == '[':
            suffix = f"{i}_{jumps[i]}"
            yield f"start_{suffix}:"
            yield "cmp byte ptr [rdi], 0"
            yield f"je end_{suffix}"
        elif command == ']':
            suffix = f"{jumps[i]}_{i}"
            yield f"jmp start_{suffix}"
            yield f"end_{suffix}:"
        elif command.startswith("."):
            yield "push rdi"
            yield "movzx rdi, byte ptr [rdi]"
            sequence = ["call putchar", "mov rdi, rax"] * n
            yield from sequence[:-1]
            yield "pop rdi"
        elif command.startswith(","):
            yield "push rdi"
            yield from ["call getchar"] * n
            yield "pop rdi"
            yield "mov byte ptr [rdi], al"
    yield "ret"
    yield '.section .note.GNU-stack,"",@progbits'


class Target(enum.Enum):
    X86_64_INTEL = enum.auto()
    X86_64_ATT = enum.auto()
    X86_32_INTEL = enum.auto()
    X86_32_ATT = enum.auto()
    # ARM
    ARM64 = enum.auto()
    ARM32 = enum.auto()
    # ...
    
    @staticmethod
    def suggest() -> Target:
        if machine() == "x86_64":
            return Target.X86_64_INTEL
        else:
            raise RuntimeError("unsupported or unknown architecture")

    @staticmethod
    def candidates() -> tuple[Target, ...]:
        if machine() == "x86_64":
            return (Target.X86_64_INTEL, Target.X86_64_ATT)
        else:
            raise RuntimeError("unsupported or unknown architecture")


def intermediate_to_asm(intermediate: list[str], *, target: Target) -> Iterator[str]:
    if target == Target.X86_64_INTEL:
        yield from generate_x86_64_intel(intermediate)
    elif target == Target.X86_64_ATT:
        yield from generate_x86_64_att(intermediate)


def bf_to_asm(input_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    with open(input_path) as input_file:
        bf_code = input_file.read()

    intermediate = bf_to_intermediate(bf_code)

    with open(output_path, 'w') as output_file:
        lines = intermediate_to_asm(intermediate, target=target)
        print(*lines, sep="\n", file=output_file)


def bf_to_shared(input_path: str, asm_path: str, output_path: str, *, target: Target = Target.suggest()) -> None:
    bf_to_asm(input_path, asm_path, target=target)
    asm_to_shared = ["cc", "-shared", "-o", output_path, asm_path]
    subprocess.run(asm_to_shared).check_returncode()
