from budivelnyk import bf_to_function, create_tape


def test_simple():
    func = bf_to_function(">+>++")
    tape = create_tape(3)
    func(tape)
    assert tape[:] == [0, 1, 2]


def test_clear():
    func = bf_to_function("[-]")
    tape = create_tape(b"a")
    func(tape)
    assert tape[:] == [0]


def test_multiply():
    func = bf_to_function("++[>+++<-]>[<+++++>-]")
    tape = create_tape(2)
    func(tape)
    assert tape[:] == [30, 0]


def test_empty_loop():
    func = bf_to_function("[]")
    tape = create_tape(bytes([0, 123]))
    func(tape)
    assert tape[:] == [0, 123]
