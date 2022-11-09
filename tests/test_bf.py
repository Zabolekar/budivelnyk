import sys
from os import path
from ctypes import CDLL
from tempfile import TemporaryDirectory
from subprocess import run, Popen, PIPE
import pytest
from budivelnyk import bf_to_shared, Target

targets = Target.candidates()

@pytest.mark.parametrize("target", targets)
def test_inc(target):
    with TemporaryDirectory() as tmp:
        bf = "tests/bf/inc.bf"
        asm = path.join(tmp, "inc.s")
        library = path.join(tmp, "libinc.so")
        bf_to_shared(bf, asm, library, target=target)

        libinc = CDLL(library)
        # We need bytes(list(...)) to prevent Python from
        # reusing the same buffer between test runs.
        buffer = bytes(list(b"Gdkkn+\x1f`rrdlakx "))
        print(buffer)
        libinc.run(buffer)
        assert buffer == b"Hello, assembly!"


@pytest.mark.parametrize("target", targets)
def test_hello(target):
    with TemporaryDirectory() as tmp:
        bf = "tests/bf/hello.bf"
        asm = path.join(tmp, "hello.s")
        library = path.join(tmp, "libhello.so")
        bf_to_shared(bf, asm, library, target=target)

        call_hello = [sys.executable, "tests/py/call_hello.py", library]
        result = run(call_hello, capture_output=True)
        result.check_returncode()
        assert result.stdout == b"hello\n"


@pytest.mark.parametrize("target", targets)
def test_echo(target):
    with TemporaryDirectory() as tmp:
        bf = "tests/bf/echo.bf"
        asm = path.join(tmp, "echo.s")
        library = path.join(tmp, "libecho.so")
        bf_to_shared(bf, asm, library, target=target)

        call_echo = [sys.executable, "tests/py/call_echo.py", library]
        with Popen(call_echo, stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
            input = b"123\n456\0"
            output, error = process.communicate(input=input, timeout=3)
            assert output == input
            assert not error


@pytest.mark.parametrize("target", targets)
def test_fibs(target):
    with TemporaryDirectory() as tmp:
        bf = "tests/bf/fibs.bf"
        asm = path.join(tmp, "fibs.s")
        library = path.join(tmp, "libfibs.so")
        bf_to_shared(bf, asm, library, target=target)

        libfibs = CDLL(library)
        buffer = bytes([0, 1, 0, 0])
        fibs = []
        for i in range(14):
            libfibs.run(buffer)
            fibs.append(buffer[0])
        # 121 because the cell overflows:
        assert fibs == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 121]
