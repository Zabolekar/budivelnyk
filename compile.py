"""
Compile bf to x86_64 asm. Cell size is one byte.
"""

from sys import argv

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

if __name__ == "__main__":
    input_path, output_path = argv[1:]
    with open(input_path) as input_file:
        bf_code = input_file.read()

    forward_jumps, backward_jumps = fill_jump_tables(bf_code)

    with open(output_path, 'w') as output_file:
        write = lambda *args: print(*args, sep="\n", file=output_file)
        write(".globl run", ".type run, @function", "run:")
        for i, c in enumerate(bf_code):
            if c == '+':
                write("incb (%rdi)")
            elif c == '-':
                write("decb (%rdi)")
            elif c == '>':
                write("incq %rdi")
            elif c == '<':
                write("decq %rdi")
            elif c == '[':
                suffix = f"{i}_{forward_jumps[i]}"
                write(f"start_{suffix}:", "cmpb $0, (%rdi)", f"je end_{suffix}")
            elif c == ']':
                suffix = f"{backward_jumps[i]}_{i}"
                write(f"jmp start_{suffix}", f"end_{suffix}:")
                # TODO: enumerate labels
            # TODO: ,.
        write("ret", '.section .note.GNU-stack,"",@progbits')
