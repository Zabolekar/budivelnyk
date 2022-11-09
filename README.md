# budivelnyk

Budivelnyk is a compiler from bf to asm. The name comes from Ukrainian *будівельник* 'builder'.

## Supported input

Currently, [bf](https://en.wikipedia.org/wiki/Brainfuck) is the only language we support. A cell is one byte large. 255 + 1 = 0 and 0 - 1 = 255. Leaving tape boundaries may or may not cause segmentation fault.

## Supported targets

Supported targets currently are:
- Linux on x86_64 (Intel syntax)
- Linux on x86_64 (AT&T syntax)

## Usage

Example usage:

```python
from budivelnyk import bf_to_asm, Target

bf_to_asm("input.bf", "output.s", target=X86_64_ATT)
```

The produced asm code can be manually assembled and linked to a shared library (currently only tested with gcc). You can also use the `bf_to_shared` helper function to create asm *and* the shared library directly from bf code:

```python
from budivelnyk import bf_to_shared

bf_to_shared("input.bf", "output.s", "liboutput.so")
```

Currently, the compiler always generates exactly one function named `run` that you can use as if its definition were `void run(char*)`. The created library can be used from any language that supports loading a shared library and passing a byte array to a function from that library.

Memory for the tape has to be allocated by the caller. This has the following advantages:
- If you know in advance that your code only requires a few bytes to run, you don't have to allocate a large tape.
- You can pre-fill the tape with input data and inspect the modified tape after the bf program exits, which leads to composable bf programs.

You may also give the program a pointer to the middle of the tape and not the beginning (but this probably has no practical use).

## Optimisations

The compiler performs simple optimisations like folding every sequence of the form `+++++` or `<<` into one assembly instruction.
