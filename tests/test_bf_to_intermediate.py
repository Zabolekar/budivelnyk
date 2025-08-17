import pytest
from budivelnyk.frontends.bf import Bf
from budivelnyk.intermediate import Loop, Subtract

def test_dead_code():
    with pytest.warns() as warnings:
        nodes = Bf.to_intermediate("[-][+]")

        assert nodes == [Loop([Subtract(1)])]

        assert len(warnings) == 1
        message = warnings[0].message.args[0]
        assert message == "Unreachable code eliminated at line 1, column 4"
