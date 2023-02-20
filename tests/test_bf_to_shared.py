import sys
from os import path
from ctypes import CDLL, create_string_buffer
from subprocess import run, Popen, PIPE
import pytest
from budivelnyk import bf_to_shared, bf_file_to_shared, Target, create_tape


targets = Target.candidates()


def generate_paths(tmp_path, name):
    asm = path.join(tmp_path, f"{name}.s")
    library = path.join(tmp_path, f"lib{name}.so")
    return asm, library


@pytest.mark.parametrize("target", targets)
def test_increment_string(target, tmp_path):
    bf = "[+>]"
    asm, library = generate_paths(tmp_path, "inc")
    bf_to_shared(bf, asm, library, target=target)

    libinc = CDLL(library)
    buffer = create_string_buffer(b"Gdkkn+\x1f`rrdlakx ")
    libinc.run(buffer)
    assert bytes(buffer) == b"Hello, assembly!"


@pytest.mark.parametrize("target", targets)
def test_zero_minus_one(target, tmp_path):
    bf = "[-]-"
    asm, library = generate_paths(tmp_path, "zmo")
    bf_to_shared(bf, asm, library, target=target)

    libzmo = CDLL(library)
    a = create_string_buffer(b"\x00", 1)
    b = create_string_buffer(b" ", 1)
    c = create_string_buffer(b"2", 1)
    libzmo.run(a)
    libzmo.run(b)
    libzmo.run(c)
    assert bytes(a) == bytes(b) == bytes(c) == b"\xff"
    d = create_string_buffer(b"1234", 4)
    libzmo.run(d)
    assert bytes(d) == b"\xff234"


@pytest.mark.parametrize("target", targets)
def test_print_hello(target, tmp_path):
    bf = "tests/bf/hello.bf"
    asm, library = generate_paths(tmp_path, "hello")
    bf_file_to_shared(bf, asm, library, target=target)

    call_hello = [sys.executable, "tests/py/call_hello.py", library]
    result = run(call_hello, capture_output=True)
    result.check_returncode()
    assert result.stdout == b"hello\n"


@pytest.mark.parametrize("target", targets)
def test_echo(target, tmp_path):
    bf = "+[,.]"
    asm, library = generate_paths(tmp_path, "echo")
    bf_to_shared(bf, asm, library, target=target)

    call_echo = [sys.executable, "tests/py/call_echo.py", library]
    with Popen(call_echo, stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
        input = b"123\n456"
        output, error = process.communicate(input=input, timeout=3)
        assert output == input + b"\0" # because we treat EOF as 0
        assert not error


@pytest.mark.parametrize("target", targets)
def test_composable_fibs(target, tmp_path):
    bf = "tests/bf/fibs.bf"
    asm, library = generate_paths(tmp_path, "fibs")
    bf_file_to_shared(bf, asm, library, target=target)

    libfibs = CDLL(library)
    buffer = create_tape(bytes([0, 1, 0, 0]))
    fibs = []
    for i in range(14):
        libfibs.run(buffer)
        byte = buffer[0]
        fibs.append(byte)
    # 121 because the cell overflows:
    assert fibs == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 121]


@pytest.mark.parametrize("target", targets)
def test_consecutive_reads(target, tmp_path):
    bf = ",,,"
    asm, library = generate_paths(tmp_path, "reads")
    bf_to_shared(bf, asm, library, target=target)

    call_reads = [sys.executable, "tests/py/call_reads.py", library]
    with Popen(call_reads, stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
        input = b"abc"
        output, error = process.communicate(input=input, timeout=3)
        assert not output
        assert not error
