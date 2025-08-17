from typing import Iterable, TypeAlias, cast
from dataclasses import dataclass
from itertools import groupby
from warnings import warn

from . import Frontend
from ..helpers import Position
from .. import intermediate


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


def _parsed_to_intermediate(bf_ast: AST) -> Iterable[intermediate.Node]:
    for (_, g) in groupby(bf_ast, type):
        group = list(g)
        count = len(group)
        specimen = group[0]
        match specimen:
            case Inc():
                yield intermediate.Add(count)  # TODO: check for byte overflow in add and subtract
            case Dec():
                yield intermediate.Subtract(count)
            case Forward():
                yield intermediate.Forward(count)
            case Back():
                yield intermediate.Back(count)
            case Output():
                yield intermediate.Output(count)
            case Input():
                yield intermediate.Input(count)
            case Loop(bf_body):
                # We optimize consecutive loops of the form [a][b][c] into [a].
                # After the execution of the first loop the current cell always
                # contains 0, so the following loops won't be executed anyway.
                if count > 1:
                    second_group = cast(Loop, group[1])
                    position = second_group.starts_at
                    assert position is not None  # It's only None if we generate nodes manually, not if we parse bf code.
                    warn(f"Unreachable code eliminated at line {position.line}, column {position.column}", RuntimeWarning)
                body = _parsed_to_intermediate(bf_body)
                yield intermediate.Loop(list(body))


class Bf(Frontend):
    @staticmethod
    def to_intermediate(code: str) -> intermediate.AST:
        parsed: AST = parse_bf(code)
        return list(_parsed_to_intermediate(parsed))
