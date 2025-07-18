from typing import Iterable, TypeAlias, cast
from dataclasses import dataclass
from itertools import groupby
from warnings import warn
from . import bf

# Indermediate language commands

class Node:
    """ Abstract syntax tree node. """
    pass

AST: TypeAlias = list[Node]

@dataclass
class Add(Node):
    """ Add constant to current cell's value. """
    constant: int

@dataclass
class Subtract(Node):
    """ Subtract constant from current cell's value. """
    constant: int

@dataclass
class Forward(Node):
    """ Add constant to cell pointer. """
    constant: int

@dataclass
class Back(Node):
    """ Subtract constant from cell pointer. """
    constant: int

@dataclass
class Output(Node):
    """ Output current cell's value multiple times. """
    count: int

@dataclass
class Input(Node):
    """ Get multiple input values and store the last one in current cell. """
    count: int

@dataclass
class Loop(Node):
    """ [] """
    body: AST


def _parsed_bf_to_intermediate(bf_ast: bf.AST) -> Iterable[Node]:
    for (_, g) in groupby(bf_ast, type):
        group = list(g)
        count = len(group)
        specimen = group[0]
        match specimen:
            case bf.Inc():
                yield Add(count)  # TODO: check for byte overflow in add and subtract
            case bf.Dec():
                yield Subtract(count)
            case bf.Forward():
                yield Forward(count)
            case bf.Back():
                yield Back(count)
            case bf.Output():
                yield Output(count)
            case bf.Input():
                yield Input(count)
            case bf.Loop(bf_body):
                # We optimize consecutive loops of the form [a][b][c] into [a].
                # After the execution of the first loop the current cell always
                # contains 0, so the following loops won't be executed anyway.
                if count > 1:
                    second_group = cast(bf.Loop, group[1])
                    position = second_group.starts_at
                    assert position is not None  # It's only None if we generate nodes manually, not if we parse bf code.
                    warn(f"Unreachable code eliminated at line {position.line}, column {position.column}", RuntimeWarning)
                body = _parsed_bf_to_intermediate(bf_body)
                yield Loop(list(body))


def bf_to_intermediate(bf_code: str) -> AST:
    parsed_bf: bf.AST = bf.parse_bf(bf_code)
    return list(_parsed_bf_to_intermediate(parsed_bf))
