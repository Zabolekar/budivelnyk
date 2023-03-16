from pathlib import PosixPath
from budivelnyk.targets.jit import jit_compiler_implemented
import pytest


jit_not_implemented = not jit_compiler_implemented()
skip_if_jit_not_implemented = pytest.mark.skipif(
    jit_not_implemented,
    reason="JIT compiler not implemented for this platform"
)


@pytest.fixture(scope='function')
def library_path(tmp_path):
    return tmp_path / "libtmp.so"
