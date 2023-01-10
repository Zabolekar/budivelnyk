from typing import Iterable, TypeAlias
from dataclasses import dataclass

# Bf commands

class Node:
    """ Bf command """
    pass

AST: TypeAlias = list[Node]

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
    body: AST


@dataclass
class _Position:
    total: int
    line: int
    column: int

def parse_bf(code: str) -> AST:
    start = _Position(total=0, line=1, column=0)
    return list(_parse_bf(code, start, expect_closing_bracket=False))


def _parse_bf(code: str, position: _Position, expect_closing_bracket: bool) -> Iterable[Node]:

    found_closing_bracket: bool = False

    while position.total < len(code):
        char = code[position.total]

        position.total += 1
        position.column += 1

        match char:
            case '+': yield Inc()
            case '-': yield Dec()
            case '>': yield Forward()
            case '<': yield Back()
            case '.': yield Output()
            case ',': yield Input()
            case '[':
                body = _parse_bf(code, position, expect_closing_bracket=True)
                yield Loop(list(body))
            case ']':
                if expect_closing_bracket:
                    found_closing_bracket = True
                    break
                else:
                    raise ValueError(f'Unexpected closing bracket at line {position.line} column {position.column}')
            case '\n':
                position.line += 1
                position.column = 0

    if expect_closing_bracket and not found_closing_bracket:
        raise ValueError('Closing bracket expected, reached end of file instead')
