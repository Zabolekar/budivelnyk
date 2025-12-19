from budivelnyk import jit_implemented
import pytest


JIT_NOT_IMPLEMENTED_MESSAGE = "JIT compiler not implemented for this platform"


@pytest.fixture(scope='function')
def library_path(tmp_path):
    return tmp_path / "libtmp.so"
