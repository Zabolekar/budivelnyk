import pytest
from budivelnyk.frontends.bf import parse_bf, Loop

def test_balanced_brackets():
    result = parse_bf("[][[[]]]")
    assert result == [Loop(body=[]), Loop(body=[Loop(body=[Loop(body=[])])])]

def test_missing_closing_brackets():
    with pytest.raises(ValueError, match="Closing bracket expected"):
        parse_bf("[[[[]]]")
    with pytest.raises(ValueError, match="Closing bracket expected"):
        parse_bf("[][[[]]")

def test_extra_closing_brackets():
    with pytest.raises(ValueError, match="Unexpected closing bracket at line 1 column 3"):
        parse_bf("[]][[[]]]")
    with pytest.raises(ValueError, match="Unexpected closing bracket at line 1 column 9"):
        parse_bf("[][[[]]]]")
    with pytest.raises(ValueError, match="Unexpected closing bracket at line 2 column 7"):
        parse_bf("[]\n[[[]]]]")
