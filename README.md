# budivelnyk

Budivelnyk is a compiler from bf to asm. The name comes from Ukrainian *будівельник* 'builder'.

## Supported Input

Currently, [bf](https://en.wikipedia.org/wiki/Brainfuck) is the only language we support. More precisely, it's the following bf variant:
- A cell is one byte large.
- 255 + 1 = 0 and 0 - 1 = 255.
- Leaving tape boundaries may or may not cause segmentation fault.
- Reading EOF with `,` saves 0 into the current cell.

Note: this bf variant is *not* Turing complete. For that, you'd need either unbounded tape or unbounded cells.

## Supported Targets

Supported targets are, in alphabetical order:

- `ARM32`: 32-bit ARM, A32 instruction set.
  - Tested on Linux, NetBSD.
- `ARM32_THUMB`: 32-bit ARM, T32 instruction set aka Thumb-2.
  - Tested on Linux, NETBSD.
- `ARM64`: 64-bit ARM aka AArch64.
  - Tested on NetBSD, OpenBSD.
- `PPC32`: 32-bit PowerPC.
  - Tested on Mac OS X Leopard.
- `RISCV64`: 64-bit RISC-V.
  - Tested on Linux.
- `X86_32_GAS_ATT`, `X86_32_GAS_INTEL`, `X86_32_NASM`: IA-32 aka i386 aka 32-bit x86.
  - Tested on OpenBSD, occasionally tested on Linux.
- `X86_64_GAS_ATT`, `X86_64_GAS_INTEL`, `X86_64_NASM`: x86_64 aka AMD64.
  - Tested on Linux, occasionally tested on FreeBSD.

As you see, `X86_32_*` and `X86_64_*` each come in three variants. They generate the same instructions, but the syntax is different:
- `X86_*_GAS_ATT` targets generate AT&T syntax as used by GAS, e.g. `incb (%rdi)`.
- `X86_*_GAS_INTEL` targets generate Intel syntax as used by GAS, e.g. `inc byte ptr [rdi]`.
- `X86_*_NASM` targets generate Intel syntax as used by NASM, e.g. `inc byte [rdi]`.

**Note:** GAS code in Intel syntax and NASM code look superficially similar, but there are important differences e.g. in how they handle the Global Offset Table.

Output of `X86_32_NASM` and `X86_64_NASM` should be assembled with NASM. For every other target, use GAS or the LLVM integrated assembler; they are almost perfectly compatible, so we don't differentiate between them.

Supported linkers are GNU `ld` and LLVM's `lld`.

## Requirements

The compiler itself only requires Python 3.10 or later to run. To run the tests, you'll also need a supported system (see above), pytest, and either GCC or Clang. We also use mypy for typechecking, but it's only required for developing the compiler, not for using it.

## Installation

1. Make sure that you have git and Python 3.10 or later installed, and that the command `cc` calls either GCC or Clang.
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

## Compiling to Assembly Language

Example usage:

```pycon
>>> from budivelnyk import bf_to_asm, Target
>>> asm = bf_to_asm("+++>--", target=Target.X86_64_GAS_INTEL)
>>> print(*asm, sep="\n")
    .intel_syntax noprefix

    .globl run
    .type run, @function
run:
    add   byte ptr [rdi], 3
    inc   rdi
    sub   byte ptr [rdi], 2
    ret

#ifdef LINUX
    .section .note.GNU-stack, "", @progbits
#endif
```

You can view the list of all targets that you can generate asm for with `tuple(Target.__members__)` and the list of all targets that are likely to run on your machine with `Target.candidates()`. The `target` parameter is optional, the default is the first target from `Target.candidates()`. For example, on an AMD64 machine, the default target is `X86_64_GAS_INTEL`.

For convenience, there is also `bf_file_to_asm_file` that accepts input and output paths:

```python
from budivelnyk import bf_file_to_asm_file, Target

bf_file_to_asm_file("input.bf", "output.s", target=Target.X86_64_ATT)
```

## Creating Shared Libraries

The produced asm code can be manually assembled and linked to a shared library. You can also use the `bf_file_to_shared` helper function to create the shared library directly from bf code:

```python
from budivelnyk import bf_file_to_shared

bf_file_to_shared("input.bf", "liboutput.so")
```

The compiler always generates exactly one function named `run` that you can use as if its definition were `void run(unsigned char*)`. The created library can be used from any language that supports loading a shared library and passing a byte array to a function from that library.

## Calling BF from C

Let's say you have created a bf shared library like this:

```python
import budivelnyk as bd
bd.bf_to_shared(".+.+.>.", "test.so")
```

If the shared library exists at compilation time, you can call it from C like this:

```c
// main.c

void run(unsigned char*);

int main()
{
    unsigned char buffer[2] = { 'A', '\n' };
    run(buffer);
}
```

Compile and run it:

```sh
cc main.c test.so -Wl,-rpath=.
./a.out
# output: ABC
```

If the shared library *doesn't* exist at compilation time, you can load it dynamically instead:

```c
// main.c

#include "dlfcn.h"

int main()
{
    unsigned char buffer[2] = { 'A', '\n' };
    void* test = dlopen("./test.so", RTLD_LAZY);
    void(*run)(unsigned char*) = dlsym(test, "run");
    run(buffer);
    dlclose(test);
}
```

Compile and run it:

```sh
cc main.c
./a.out
# output: ABC
```

## Tapes

Memory for the tape has to be allocated by the caller. This has the following advantages:
- If you know in advance that your code only requires a few bytes to run, you don't have to allocate a large tape.
- You can pre-fill the tape with input data and inspect the modified tape after the bf program exits, which leads to composable bf programs.

The disadvantages, compared to a hypothetical implementation that allocates more tape when needed, are:
- If you *don't* know in advance how much tape your bf code requires, which is likely to be the case with most non-trivial programs, you have to guess. If your guess is too low, the program might crash, and if your guess is too high, you'll waste memory. Worse, the required tape length can't always be determined empirically because it might depend on user input.

Note that some bf programs, e.g. `+[>+]`, require an infinitely long tape. They can't be executed on a real computer. Allocating more tape on demand won't solve that.

## Tapes in Python

The proper way to create a tape is to use the `tape_of_size(int) -> Tape` and `tape_with_contents(bytes|bytearray) -> Tape` functions we provide,
which return a mutable `ctypes` array of unsigned bytes:

```python
from ctypes import CDLL
from budivelnyk import make_tape

mylib = CDLL("./mylib.so")
tape = tape_with_contents(b"test")  # creates a tape with 4 cells, copies 't', 'e', 's', 't' to it
my_lib.run(tape)

my_other_lib = CDLL("./myotherlib.so")
other_tape = tape_of_size(4)  # creates a tape with 4 cells, initialized to zero
my_other_lib.run(other_tape)
```

The `as_tape` function can be used to wrap an existing mutable buffer, e.g. a `numpy` array:

```python
import numpy as np
import budivelnyk as bd

arr = np.array([1,0,0], dtype=np.uint8)
tape = bd.as_tape(arr)
print(tape[:]) # [1, 0, 0]
```

The function is very lenient and assumes that you know what you're doing. If your `numpy` array is e.g. not contiguous in memory or its elements are larger than 1 byte, there will be no error messages.

By default, it uses the `len` of its argument as the tape size. If it's unsuitable, you can also provide a `size` argument. In the following example, the buffer contains 12 bytes, but its `len` is one:

```pycon
>>> import numpy as np
>>> import budivelnyk as bd
>>> arr = np.array([[1,0,-1]], dtype=np.int32)
>>> bd.as_tape(arr)[:]
[1]
>>> bd.as_tape(arr, 3 * 4)[:]
[1, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255]
```

### Warning about Python and Bytes

Sometimes it seems convenient to use a `bytes` object as the function argument:

```python
from ctypes import CDLL

my_lib = CDLL("./mylib.so")
my_lib.run(b"test")
```

If your code doesn't modify the tape, it may work, but do not rely on this. **Do not ever** do this if your code modifies the tape. This will cause bizarre bugs, e.g. literals like `b"\0"` evaluating to `b"\xff"`. The Python interpreter expects all `bytes` objects to be immutable and reuses them.

## `bf_to_function` and Experimental JIT Compilation

Use `bf_to_function` to directly create a Python function from bf code:

```pycon
>>> import budivelnyk as bd
>>> tape = bd.tape_with_contents(bytes([5,6]))
>>> add = bd.bf_to_function(">[-<+>]")
>>> add(tape)
>>> tape[:]
[11, 0]
```

When you call `bf_to_function` with `use_jit=True` (the default), it generates runnable machine code in memory without using an external assembler or linker. This currently only works on x86_64 Linux. On every other platform, `bf_to_function` should be called with `use_jit=False`, in which case it *does* use an external assembler and linker.

## Optimisations

The compiler performs simple optimisations like folding every sequence of the form `+++++` or `<<` into one assembly instruction.

The compiler also eliminates some unreachable code. For example, in constructions like `[-][+]` the second loop will not be executed, as the cell already contains 0, so it's safe to skip it during compilation. People usually don't write unreachable
code on purpose other than for testing the compiler, so we emit a warning.

## Frequently Asked Questions

**Q:** What are the goals of the project?

**A:** The main goal is to learn how different computer architectures work.
