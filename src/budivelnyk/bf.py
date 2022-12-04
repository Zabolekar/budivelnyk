from typing import Iterable, TypeAlias
from dataclasses import dataclass

# Bf commands

class Node:
    """ Bf command """
    pass

class Inc(Node):
    """ + """
    pass

class Dec(Node):
    """ - """
    pass

class Forward(Node):
    """ > """
    pass

class Back(Node):
    """ < """
    pass

class Output(Node):
    """ . """
    pass

class Input(Node):
    """ , """
    pass

@dataclass
class Loop(Node):
    """ [] """
    body: list[Node]


AST: TypeAlias = list[Node]


def parse_bf(code: str) -> AST:
    sequence: Iterable[str] = iter(code)
    return list(_parse_bf(sequence, expect_closing_bracket=False))


def _parse_bf(sequence: Iterable[str], expect_closing_bracket: bool) -> Iterable[Node]:
    for char in sequence:
        match char:
            case '+': yield Inc()
            case '-': yield Dec()
            case '>': yield Forward()
            case '<': yield Back()
            case '.': yield Output()
            case ',': yield Input()
            case '[':
                body = _parse_bf(sequence, expect_closing_bracket=True)
                yield Loop(list(body))
            case ']':
                if expect_closing_bracket:
                    break
                else:
                    raise RuntimeError('Unexpected closing bracket')
                    # TODO: add line number and position, test it
    else:
        if expect_closing_bracket:
            raise RuntimeError('Closing bracket expected') 
