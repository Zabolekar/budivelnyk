from __future__ import annotations
from typing import Iterable, TypeAlias
from dataclasses import dataclass, replace


@dataclass
class Position:
    total: int
    line: int
    column: int

    def copy(self) -> Position:
        return replace(self)

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
    starts_at: Position|None = None
    # `starts_at` is position in source code. If there is no source code
    # (e.g. if we generate bf AST directly), it should be None.
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Loop):
            return NotImplemented
        return self.body == other.body

def parse_bf(code: str) -> AST:
    start = Position(total=0, line=1, column=0)
    return list(_parse_bf(code, start, expect_closing_bracket=False))


def _parse_bf(code: str, position: Position, expect_closing_bracket: bool) -> Iterable[Node]:

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
                starting_position = position.copy()
                body = _parse_bf(code, position, expect_closing_bracket=True)
                yield Loop(list(body), starting_position)
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
