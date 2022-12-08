# budivelnyk

Budivelnyk is a compiler from bf to asm. The name comes from Ukrainian *будівельник* 'builder'.

## Supported Input

Currently, [bf](https://en.wikipedia.org/wiki/Brainfuck) is the only language we support. More precisely, it's the following bf variant:
- A cell is one byte large.
- 255 + 1 = 0 and 0 - 1 = 255.
- Leaving tape boundaries may or may not cause segmentation fault.
- Reading EOF with `,` saves 0 into the current cell.

## Supported Targets

Supported targets currently are:
- Linux on x86_64 (Intel syntax)
- Linux on x86_64 (AT&T syntax)
- NetBSD on ARM64
- OpenBSD on ARM64
- Linux on RISCV64

## Requirements

The compiler itself only requires Python 3.10 to run. To run the tests, you'll also need a supported system (see above), pytest, and GCC. We also use mypy for typechecking.

## Installation

1. Make sure that you have git, GCC and Python 3.10 installed.
2. Clone the repository with `git clone https://github.com/Zabolekar/budivelnyk/` and switch into the folder with `cd budivelnyk`.
3. Create an environment, activate it and install pytest and budivelnyk itself. There are many ways to do that, the simplest is the following:

```sh
python3 -m venv ~/venvs/budivelnyk
. ~/venvs/budivelnyk/bin/activate
pip install pytest
pip install -e .
```

4. Run `pytest` to verify that everything works.

Be aware that the tests that require executing machine code are only performed for the platform you run them on, e.g. tests for ARM64 won't be performed on x86_64.

## Usage

Example usage:

```pycon
>>> from budivelnyk import bf_to_asm
>>> asm = bf_to_asm("+++>--", target=Target.X86_64_INTEL)
>>> print(*asm, sep="\n")
    .intel_syntax noprefix

    .globl run
    .type run, @function
run:
    add   byte ptr [rdi], 3
    inc   rdi
    sub   byte ptr [rdi], 2
    ret

    .section .note.GNU-stack, "", @progbits
```

You can view the list of all targets that you can generate asm for with `tuple(Target.__members__)` and the list of all targets that can run on your hardware with `Target.candidates()`. The `target` parameter is optional, the default is the first target from `Target.candidates()`.

For convenience, there is also `bf_file_to_asm_file` that accepts input and output paths:

```python
from budivelnyk import bf_file_to_asm_file, Target

bf_file_to_asm_file("input.bf", "output.s", target=Target.X86_64_ATT)
```

The produced asm code can be manually assembled and linked to a shared library (currently only tested with GCC). You can also use the `bf_file_to_shared` helper function to create asm *and* the shared library directly from bf code:

```python
from budivelnyk import bf_file_to_shared

bf_file_to_shared("input.bf", "output.s", "liboutput.so")
```

Currently, the compiler always generates exactly one function named `run` that you can use as if its definition were `void run(char*)`. The created library can be used from any language that supports loading a shared library and passing a byte array to a function from that library.

Memory for the tape has to be allocated by the caller. This has the following advantages:
- If you know in advance that your code only requires a few bytes to run, you don't have to allocate a large tape.
- You can pre-fill the tape with input data and inspect the modified tape after the bf program exits, which leads to composable bf programs.

You may also give the program a pointer to the middle of the tape and not the beginning (but this probably has no practical use).

### Warning about Python, Ctypes, and Bytes

If your bf code doesn't modify the tape, it's convenient to use a `bytes` object as the function argument:

```python
from ctypes import CDLL

mylib = CDLL("./mylib.so")
mylib.run(b"test")
```

**Do not ever** do this if your code modifies the tape.  This will cause bizarre bugs, e.g. literals like `b"\0"` evaluating to `b"\xff"`. The Python interpreter expects all `bytes` objects to be immutable and reuses them. There are many ways to create mutable storage in Python, e.g. with `ctypes.create_string_buffer`, or by creating a contiguous numpy array and setting `mylib.run.argtypes` to `(np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, flags="C"),)`.

## Optimisations

The compiler performs simple optimisations like folding every sequence of the form `+++++` or `<<` into one assembly instruction.

The compiler also eliminates some unreachable code. For example, in constructions like `[-][+]` the second loop will not be executed, as the cell already contains 0, so it's safe to skip it during compilation. People usually don't write unreachable
code on purpose other than for testing the compiler, so we emit a warning.

## Frequently Asked Questions

No questions have been asked yet.
