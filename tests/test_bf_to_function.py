from budivelnyk import bf_to_function, create_tape


def test_simple():
    func = bf_to_function(">+>++")
    tape = create_tape(3)
    func(tape)
    assert tape[:] == [0, 1, 2]
