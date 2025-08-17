from typing import Callable, Iterator, Type
import shutil
from ctypes import CDLL
from platform import system
from tempfile import NamedTemporaryFile

from .tape import Tape
from .frontends import Frontend
from .backends import Backend
from .backends.jit import intermediate_to_function, UseJIT, jit_implemented
from .intermediate import AST
from .helpers import run_and_maybe_fail


def to_function(frontend: Type[Frontend], code: str, *, use_jit: UseJIT = UseJIT.default()) -> Callable[[Tape], None]:
    intermediate: AST = frontend.to_intermediate(code)
    match use_jit:
        case UseJIT.LIBC:
            return intermediate_to_function(intermediate, linux_syscalls=False)
        case UseJIT.SYSCALLS:
            return intermediate_to_function(intermediate, linux_syscalls=True)
        case UseJIT.NO:
            with NamedTemporaryFile() as library_file:
                library_path = library_file.name
                _intermediate_to_shared(intermediate, library_path, Backend.suggest())
                func = CDLL(library_path).run
                func.restype = None
                return func


def to_asm(frontend: Type[Frontend], code: str, *, backend: Backend = Backend.suggest()) -> Iterator[str]:
    intermediate: AST = frontend.to_intermediate(code)
    yield from backend.intermediate_to_asm(intermediate)


def file_to_asm_file(frontend: Type[Frontend], input_path: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None:
    with open(input_path) as input_file:
        code = input_file.read()

    _to_asm_file(frontend, code, output_path, backend=backend)


def to_shared(frontend: Type[Frontend], code: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None:
    intermediate: AST = frontend.to_intermediate(code)
    _intermediate_to_shared(intermediate, output_path, backend)


def file_to_shared(frontend: Type[Frontend], input_path: str, output_path: str, *, backend: Backend = Backend.suggest()) -> None:
    with open(input_path) as input_file:
        code = input_file.read()

    to_shared(frontend, code, output_path, backend=backend)


def _intermediate_to_shared(intermediate: AST, output_path: str, backend: Backend) -> None:
    nasm: bool = backend in (Backend.X86_32_NASM, Backend.X86_64_NASM, Backend.X86_64_LINUX_SYSCALLS_NASM)
    if not shutil.which("cc"):
        raise RuntimeError("cc not found")
    if nasm and not shutil.which("nasm"):
        raise RuntimeError("nasm not found")

    with (NamedTemporaryFile(suffix=".s") as asm_file,
          NamedTemporaryFile(suffix=".o") as object_file):
        asm_path, object_path = asm_file.name, object_file.name
        _intermediate_to_asm_file(intermediate, asm_path, backend=backend)
        # assemble:
        if nasm:
            bits = 32 if backend == Backend.X86_32_NASM else 64
            FORMAT = "-felf" + str(bits)
            run_and_maybe_fail("nasm", FORMAT, asm_path, "-o", object_path)
        else:
            run_and_maybe_fail("cc", "-c", asm_path, "-o", object_path)
        # link:
        SHARED = "-dynamiclib" if system() == "Darwin" else "-shared"
        run_and_maybe_fail("cc", "-z", "noexecstack", SHARED, object_path, "-o", output_path)


def _intermediate_to_asm_file(intermediate: AST, output_path: str, backend: Backend) -> None:
    lines = backend.intermediate_to_asm(intermediate)

    with open(output_path, 'w') as output_file:
        print(*lines, sep="\n", file=output_file)


def _to_asm_file(frontend: Type[Frontend], code: str, output_path: str, backend: Backend) -> None:
    lines = to_asm(frontend, code, backend=backend)

    with open(output_path, 'w') as output_file:
        print(*lines, sep="\n", file=output_file)
