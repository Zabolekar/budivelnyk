from pathlib import PosixPath
from budivelnyk.targets.jit import jit_compiler_implemented
import pytest

jit_not_implemented = not jit_compiler_implemented()
skip_if_jit_not_implemented = pytest.mark.skipif(
    jit_not_implemented,
    reason="JIT compiler not implemented for this platform"
)

def generate_paths(tmp_path: PosixPath, name: str):
    asm = tmp_path / f"{name}.s"
    library = tmp_path / f"lib{name}.so"
    return asm, library
