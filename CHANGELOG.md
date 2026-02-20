This file only describes the most important changes. A more detailed history
can be found in the version control log.

# 0.1.0

- Darwin/x86_64 support
- Backend descriptions rewritten and unified (instruction set + input/output + executable format + asm syntax)
- Added `Head` and `Machine` types
- Added `shared_to_function`, a helper function for loading shared libraries
- The generated `run` function now returns the head position after the machine has halted
- Python 3.11 required (3.10 might still work, but we don't test it anymore)

# 0.0.9

- Simplified and documented executable stack handling
- Warnings are now able to tell the position where they occured
- Infrastracture for multiple frontends (that is, not only bf)

# 0.0.8

- Linux syscalls (as an alternative to libc calls) supported on x86_64
- Different API for creating tapes and for the experimental JIT

# 0.0.7

- NASM support on i386 and AMD64
- 32-bit PowerPC support

# 0.0.6

- `bf_to_function` and experimental JIT on x86_64 Linux.
- `bf_to_shared` and `bf_file_to_shared` no longer require the user to provide
a path to asm file.

# 0.0.5

- i386 support.

# 0.0.4

- 32-bit ARM (as well as Thumb-2) support.

# 0.0.3

- RISCV64 support.
- Conformance to standard bf: EOF is treated as 0.

# 0.0.2

- 64-bit ARM support.
- On AMD64, Intel syntax is supported and becomes the default.
- Optimizations for `++`, `<<<` and similar sequences.
- Dead code elimination for consecutve loops.

# 0.0.1 (Initial Version)

- Compile bf (one-byte-cell variant) to AT&T syntax AMD64 assembly,
which can be assembled to a shared library.
