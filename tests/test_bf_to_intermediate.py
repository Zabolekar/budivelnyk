import sys
from os import path
import pytest
from budivelnyk import bf_to_intermediate
from budivelnyk.intermediate import Loop, Decrement

def test_dead_code():
    with pytest.warns() as warnings:
        nodes = bf_to_intermediate("[-][+]")

        assert nodes == [Loop([Decrement()])]

        assert len(warnings) == 1
        message = warnings[0].message.args[0]
        assert message == "Unreachable code detected and eliminated"
