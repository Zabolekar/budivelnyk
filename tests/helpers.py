from budivelnyk import jit_implemented
import pytest


skip_if_jit_not_implemented = pytest.mark.skipif(
    not jit_implemented,
    reason="JIT compiler not implemented for this platform"
)


@pytest.fixture(scope='function')
def library_path(tmp_path):
    return tmp_path / "libtmp.so"
