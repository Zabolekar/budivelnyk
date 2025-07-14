import sys
from ctypes import CDLL
from subprocess import run, Popen, PIPE, TimeoutExpired
import pytest
from budivelnyk import bf_to_shared, bf_file_to_shared, Backend, tape_with_contents
from helpers import library_path


backends = Backend.candidates()


@pytest.mark.parametrize("backend", backends)
def test_increment_string(backend, library_path):
    bf = "[+>]"
    bf_to_shared(bf, library_path, backend=backend)

    libinc = CDLL(library_path)
    buffer = tape_with_contents(b"Gdkkn+\x1f`rrdlakx \x00")
    libinc.run(buffer)
    assert bytes(buffer) == b"Hello, assembly!\x00"


@pytest.mark.parametrize("backend", backends)
def test_zero_minus_one(backend, library_path):
    bf = "[-]-"
    bf_to_shared(bf, library_path, backend=backend)

    libzmo = CDLL(library_path)
    a = tape_with_contents(b"\x00")
    b = tape_with_contents(b" ")
    c = tape_with_contents(b"2")
    libzmo.run(a)
    libzmo.run(b)
    libzmo.run(c)
    assert a[:] == b[:] == c[:] == [255]
    d = tape_with_contents(b"1234")
    libzmo.run(d)
    assert bytes(d) == b"\xff234"


@pytest.mark.parametrize("backend", backends)
def test_print_hello(backend, library_path):
    bf = "tests/bf/hello.bf"
    bf_file_to_shared(bf, library_path, backend=backend)

    call_hello = [sys.executable, "tests/py/call_hello.py", library_path]
    result = run(call_hello, capture_output=True)
    result.check_returncode()
    assert result.stdout == b"hello\n"


@pytest.mark.parametrize("backend", backends)
def test_tee(backend, library_path):
    bf = "+[,.]"
    bf_to_shared(bf, library_path, backend=backend)

    call_tee = [sys.executable, "tests/py/call_tee.py", library_path]
    with Popen(call_tee, stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
        input = b"123\n456"
        try:
            output, error = process.communicate(input=input, timeout=3)
            assert not error
            assert output == input + b"\0" # because we treat EOF as 0
        except TimeoutExpired as e:
            process.kill()
            assert False, f"process still runs after {e.timeout} s"


@pytest.mark.parametrize("backend", backends)
def test_composable_fibs(backend, library_path):
    bf = "tests/bf/fibs.bf"
    bf_file_to_shared(bf, library_path, backend=backend)

    libfibs = CDLL(library_path)
    buffer = tape_with_contents(bytes([0, 1, 0, 0]))
    fibs = []
    for i in range(14):
        libfibs.run(buffer)
        byte = buffer[0]
        fibs.append(byte)
    # 121 because the cell overflows:
    assert fibs == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 121]


@pytest.mark.parametrize("backend", backends)
def test_consecutive_reads(backend, library_path):
    bf = ",,,"
    bf_to_shared(bf, library_path, backend=backend)

    call_reads = [sys.executable, "tests/py/call_reads.py", library_path]
    with Popen(call_reads, stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
        input = b"abc"
        try:
            output, error = process.communicate(input=input, timeout=3)
            assert not output and not error
        except TimeoutExpired as e:
            process.kill()
            assert False, f"process still runs after {e.timeout} s"
