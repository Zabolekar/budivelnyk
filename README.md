# budivelnyk

Budivelnyk is a compiler from bf to asm. The name comes from Ukrainian *будівельник* 'builder'.

## Supported Frontends

Currently, [bf](https://en.wikipedia.org/wiki/Brainfuck) is the only language we support. More precisely, it's the following bf variant:
- A cell is one byte large.
- 255 + 1 = 0 and 0 - 1 = 255.
- Leaving tape boundaries may or may not cause segmentation fault.
- Reading EOF with `,` saves 0 into the current cell.

Note: this bf variant is *not* Turing complete. For that, you'd need either unbounded tape or unbounded cells.

## Supported Backends

Supported backends are, in alphabetical order:

- `ARM32_LIBC_ELF_USUAL`: 32-bit ARM, A32 instruction set.
  - Tested on Linux, NetBSD.
- `ARM32_THUMB_LIBC_ELF_USUAL`: 32-bit ARM, T32 instruction set aka Thumb-2.
  - Tested on Linux, NETBSD.
- `ARM64_LIBC_ELF_USUAL`: 64-bit ARM aka AArch64.
  - Tested on NetBSD, OpenBSD.
- `PPC32_LIBC_MACHO_USUAL`: 32-bit PowerPC.
  - Tested on Mac OS X Leopard.
- `RISCV64_LIBC_ELF_USUAL`: 64-bit RISC-V.
  - Tested on Linux.
- `X86_32_LIBC_ELF_GAS_ATT`, `X86_32_LIBC_ELF_GAS_INTEL`, `X86_32_LIBC_ELF_NASM`: IA-32 aka i386 aka 32-bit x86.
  - Tested on OpenBSD, occasionally tested on Linux.
- `X86_64_LIBC_ELF_GAS_ATT`, `X86_64_LIBC_ELF_GAS_INTEL`, `X86_64_LIBC_ELF_NASM`: x86_64 aka AMD64 for ELF-based systems.
  - Tested on Linux, occasionally tested on FreeBSD.
- `X86_64_LIBC_MACHO_GAS_ATT`, `X86_64_LIBC_MACHO_GAS_INTEL`, `X86_64_LIBC_MACHO_NASM`: x86_64 aka AMD64 for macOS.
  - Tested on macOS Mojave.
- `X86_64_LINUX_SYSCALLS_ELF_GAS_ATT`, `X86_64_LINUX_SYSCALLS_ELF_GAS_INTEL`, `X86_64_LINUX_SYSCALLS_ELF_NASM`: x86_64 aka AMD64, using Linux system calls instead of C library functions.
  - Linux only.

A backend name consists of four fields:
1. Instruction set, e.g. `X86_64`, `RISCV64`, `ARM32`, `ARM32_THUMB`
2. What to use for input and output, e.g. `LIBC` or `LINUX_SYSCALLS`
3. The intended executable format, e.g. `ELF` or `MACHO`. We don't produce any executable files ourselves - only with external assemblers and linkers - but the intended format still affects the assembly language we generate, e.g. symbol names and section names.
4. The assembly language syntax. For example, the `X86_32_*`  and `X86_64_*` targets have three varians each. They will produce the same instructions when assembled, but are written differently:
- `X86_*_GAS_ATT` backends generate AT&T syntax as used by GAS, e.g. `incb (%rdi)`.
- `X86_*_GAS_INTEL` backends generate Intel syntax as used by GAS, e.g. `inc byte ptr [rdi]`.
- `X86_*_NASM` backends generate Intel syntax as used by NASM, e.g. `inc byte [rdi]`.

**Note**: GAS code in Intel syntax and NASM code look superficially similar, but there are important differences e.g. in how they handle the Global Offset Table.

The `USUAL` syntax is a catch-all term for "we only use one syntax for this platform, and don't know if it has a name".

To make backend handling easier, a `Backend` object has a public attribute for each field:

```pycon
>>> from budivelnyk import Backend
>>> riscv64 = Backend.RISCV64_LIBC_ELF_USUAL
>>> riscv64.instruction_set
<InstructionSet.RISCV64: 5>
>>> riscv64.io
<InputOutput.LIBC: 1>
>>> riscv64.format
<Format.ELF: 1>
>>> riscv64.syntax
<Syntax.USUAL: 4>
```

### Assembling and Linking the Output

Output of `X86_*_NASM` should be assembled with NASM. For every other backend, use GAS or the LLVM integrated assembler; they are almost perfectly compatible, so we don't differentiate between them.

Supported linkers are GNU `ld` and LLVM's `lld`.

If you assemble and link the asm code produced by budivelnyk and see a warning about executable stack, add the `-z noexecstack` linker flag.
See [executable_stack.md](executable_stack.md) for details.

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
>>> from budivelnyk import Bf, Backend
>>> asm = Bf.to_asm("+++>--", backend=Backend.X86_64_LIBC_ELF_GAS_INTEL)
>>> print(*asm, sep="\n")
    .intel_syntax noprefix

    .globl run
    .type run, @function
run:
    add   byte ptr [rdi], 3
    inc   rdi
    sub   byte ptr [rdi], 2
    ret
```

You can view the list of all backends that you can generate asm for with `list(Backend)` and the list of all backends that are likely to generate code that runs on your machine with `Backend.candidates()`. The `backend` parameter is optional, the default is the first backend from `Backend.candidates()`. For example, on an AMD64 machine running Linux or *BSD, the default backend is `X86_64_LIBC_ELF_GAS_INTEL`.

For convenience, there is also `Bf.file_to_asm_file` that accepts input and output paths:

```python
from budivelnyk import Bf, Backend

Bf.file_to_asm_file("input.bf", "output.s", backend=Backend.X86_64_LIBC_ELF_GAS_ATT)
```

## Creating Shared Libraries

The produced asm code can be manually assembled and linked to a shared library. You can also use the `Bf.to_shared` and `Bf.file_to_shared` helper functions to create the shared library directly from bf code:

```python
from budivelnyk import Bf

Bf.file_to_shared("input.bf", "liboutput.so")
```

The compiler always generates exactly one function named `run` that you can use as if its definition were `unsigned char* run(unsigned char*)`. The created library can be used from any language that supports loading a shared library, passing a pointer to a byte array to a function from that library, and interpreting its return value as another pointer to a byte array. In bf terms (or Turing machine terms), the byte array in question is called a *tape* and its elements are called *cells*. A machine has a *head* positioned over a cell. The input pointer represents the head position before the execution starts, and the returned pointer represents the head position after the execution halts.

Normally, you shouldn't need the return value, and can simply declare the function as `void run(unsigned char*)`. Knowing the head position after the machine has finished running is, however, useful if you need to decompose a large computation into smaller steps: after each step, you can inspect the tape, log the elapsed time etc., and then pass the saved return value to the next function.

## Calling BF from C

Let's say you have created a bf shared library like this:

```python
import budivelnyk as bd
bd.Bf.to_shared(".+.+.>.", "test.so")
```

If the shared library exists at compilation time, you can call it from C like this:

```c
// main.c

void run(unsigned char*); // ignoring the return value

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

## Calling BF from Python

The recommended way to create a tape is to use the `tape_of_size(int) -> Tape` and `tape_with_contents(bytes|bytearray) -> Tape` functions. A `Tape` is a mutable `ctypes` array of unsigned bytes, a `Head` is a `ctypes` pointer to an unsigned byte, presumably to an element of such an array. The type `Machine` is an alias for `Callable[[Tape|Head], Head]`.

The recommended way to call a shared bf library from Python is to load it with the `shared_to_function(str) -> Machine`, which is a wrapper around `ctypes.CDLL` that takes care of the return type.

```python
import budivelnyk as bd

run = bd.shared_to_function("./mylib.so")

tape = bd.tape_with_contents(b"test")  # creates a tape with 4 cells, copies 't', 'e', 's', 't' to it
run(tape)  # ignoring the return value

other_tape = bd.tape_of_size(4)  # creates a tape with 4 cells, initialized to zero
run(other_tape)
```

The `as_tape(buffer, size: int) -> Tape` function can be used to wrap an existing mutable buffer, e.g. a `numpy` array:

```python
import numpy as np
import budivelnyk as bd

arr = np.array([1,0,0], dtype=np.uint8)
tape = bd.as_tape(arr, 3)
print(tape[:]) # [1, 0, 0]
```

The function is very lenient and assumes that you know what you're doing. If your `numpy` array is e.g. not contiguous in memory, there will be no error messages. The `size` argument should be the tape length in bytes, which may be different from the the `len` of the buffer. In the following example, the buffer contains 12 bytes, but its `len` is one:

```pycon
>>> import numpy as np
>>> import budivelnyk as bd
>>> arr = np.array([[1,0,-1]], dtype=np.int32)
>>> bd.as_tape(arr, len(arr))[:]
[1]
>>> bd.as_tape(arr, arr.nbytes)[:]
[1, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255]
```

### Warning about Python and Bytes

Sometimes it seems convenient to use a `bytes` object as the function argument:

```python
from budivelnyk import shared_to_function

run = shared_to_function("./mylib.so")
run(b"test")
```

If your code doesn't modify the tape, it may work, but do not rely on this. **Do not ever** do this if your code modifies the tape. This will cause bizarre bugs, e.g. literals like `b"\0"` evaluating to `b"\xff"`. The Python interpreter expects all `bytes` objects to be immutable and reuses them.

## `Bf.to_function` and Experimental JIT Compilation

Use `Bf.to_function` to directly create a Python function from bf code:

```pycon
>>> import budivelnyk as bd
>>> tape = bd.tape_with_contents(bytes([5,6]))
>>> add = bd.Bf.to_function(">[-<+>]")
>>> add(tape)
>>> tape[:]
[11, 0]
```

The function `Bf.to_function` has an optional `use_jit` parameter. 

When called with `use_jit=bd.UseJIT.SYSCALLS` (the default on x86_64 Linux) or `use_jit=bd.UseJIT.LIBC`, it generates runnable machine code in memory without using an external assembler or linker. Code generated with `bd.UseJIT.SYSCALLS` uses system calls and code generated with `bd.UseJIT.LIBC` calls functions from the C library. Both options currently only work on x86_64 Linux.

When called with `use_jit=bd.UseJIT.NO` (the default on every other platform), the fallback implementation is used: it creates temporary assembly files, calls an external assembler and linker to create a shared library, then loads the function from the shared library.

## Optimisations

The compiler performs simple optimisations like folding every sequence of the form `+++++` or `<<` into one assembly instruction.

The compiler also eliminates some unreachable code. For example, in constructions like `[-][+]` the second loop will not be executed, as the cell already contains 0, so it's safe to skip it during compilation. People usually don't write unreachable
code on purpose other than for testing the compiler, so we emit a warning.

## Summary and Type Signatures

To summarize, the package provides the following types:

- `Tape`, `Head`, `Machine`, `Backend`, `UseJIT`

And the following bf-specific functions:

- `Bf.to_function(code: str, *, use_jit: UseJIT = UseJIT.default()) -> Machine`
- `Bf.to_asm(code: str, *, backend: Backend = Backend.suggest()) -> Iterator[str]`
- `Bf.file_to_asm_file(input_path: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None`
- `Bf.to_shared(code: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None`
- `Bf.file_to_shared(input_path: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None`

And the following frontend-independent function:

- `shared_to_function(library_path: str) -> Machine`

And the following global variable:

- `jit_implemented: bool` (true on x86_64 Linux, false otherwise)

## Frequently Asked Questions

**Q:** What are the goals of the project?

**A:** The main goal is to learn how different computer architectures work.
