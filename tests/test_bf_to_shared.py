import sys
import platform
from ctypes import CDLL
from subprocess import run, Popen, PIPE, TimeoutExpired
import pytest
from budivelnyk import bf_to_shared, bf_file_to_shared, Target, make_tape
from helpers import library_path


targets = Target.candidates()
syscalls = (False, True) if platform.system() == "Linux" else (False,)


@pytest.mark.parametrize("target", targets)
@pytest.mark.parametrize("syscalls", syscalls)
def test_increment_string(target, syscalls, library_path):
    bf = "[+>]"
    bf_to_shared(bf, library_path, target=target, linux_syscalls=syscalls)

    libinc = CDLL(library_path)
    buffer = make_tape(b"Gdkkn+\x1f`rrdlakx \x00")
    libinc.run(buffer)
    assert bytes(buffer) == b"Hello, assembly!\x00"


@pytest.mark.parametrize("target", targets)
@pytest.mark.parametrize("syscalls", syscalls)
def test_zero_minus_one(target, syscalls, library_path):
    bf = "[-]-"
    bf_to_shared(bf, library_path, target=target, linux_syscalls=syscalls)

    libzmo = CDLL(library_path)
    a = make_tape(b"\x00")
    b = make_tape(b" ")
    c = make_tape(b"2")
    libzmo.run(a)
    libzmo.run(b)
    libzmo.run(c)
    assert a[:] == b[:] == c[:] == [255]
    d = make_tape(b"1234")
    libzmo.run(d)
    assert bytes(d) == b"\xff234"


@pytest.mark.parametrize("target", targets)
@pytest.mark.parametrize("syscalls", syscalls)
def test_print_hello(target, syscalls, library_path):
    bf = "tests/bf/hello.bf"
    bf_file_to_shared(bf, library_path, target=target, linux_syscalls=syscalls)

    call_hello = [sys.executable, "tests/py/call_hello.py", library_path]
    result = run(call_hello, capture_output=True)
    result.check_returncode()
    assert result.stdout == b"hello\n"


@pytest.mark.parametrize("target", targets)
@pytest.mark.parametrize("syscalls", syscalls)
def test_tee(target, syscalls, library_path):
    bf = "+[,.]"
    bf_to_shared(bf, library_path, target=target, linux_syscalls=syscalls)

    call_tee = [sys.executable, "tests/py/call_tee.py", library_path]
    with Popen(call_tee, stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
        input = b"123\n456"
        try:
            output, error = process.communicate(input=input, timeout=3)
            assert output == input + b"\0" # because we treat EOF as 0
            assert not error
        except TimeoutExpired as e:
            process.kill()
            assert False, f"process still runs after {e.timeout} s"


@pytest.mark.parametrize("target", targets)
@pytest.mark.parametrize("syscalls", syscalls)
def test_composable_fibs(target, syscalls, library_path):
    bf = "tests/bf/fibs.bf"
    bf_file_to_shared(bf, library_path, target=target, linux_syscalls=syscalls)

    libfibs = CDLL(library_path)
    buffer = make_tape(bytes([0, 1, 0, 0]))
    fibs = []
    for i in range(14):
        libfibs.run(buffer)
        byte = buffer[0]
        fibs.append(byte)
    # 121 because the cell overflows:
    assert fibs == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 121]


@pytest.mark.parametrize("target", targets)
@pytest.mark.parametrize("syscalls", syscalls)
def test_consecutive_reads(target, syscalls, library_path):
    bf = ",,,"
    bf_to_shared(bf, library_path, target=target, linux_syscalls=syscalls)

    call_reads = [sys.executable, "tests/py/call_reads.py", library_path]
    with Popen(call_reads, stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
        input = b"abc"
        try:
            output, error = process.communicate(input=input, timeout=3)
            assert not output and not error
        except TimeoutExpired as e:
            process.kill()
            assert False, f"process still runs after {e.timeout} s"
