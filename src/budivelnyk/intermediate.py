from typing import TypeAlias
from dataclasses import dataclass
from itertools import groupby
from warnings import warn
from . import bf

# Indermediate language commands

class Node:
    """ Abstract syntax tree node. """
    pass

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
    body: list[Node]

AST: TypeAlias = list[Node]

def _parsed_bf_to_intermediate(bf_ast: bf.AST) -> AST:
    result: AST = []
    for (_, g) in groupby(bf_ast, lambda node: type(node)):
        group = list(g)
        count = len(group)
        specimen = group[0]
        match specimen:
            case bf.Inc():
                result.append(Add(count))
            case bf.Dec():
                result.append(Subtract(count))
            case bf.Forward():
                result.append(Forward(count))
            case bf.Back():
                result.append(Back(count))
            case bf.Output():
                result.append(Output(count))
            case bf.Input():
                result.append(Input(count))
            case bf.Loop(bf_body):
                # We optimize consecutive loops of the form [a][b][c] into [a].
                # After the execution of the first loop the current cell always
                # contains 0, so the following loops won't be executed anyway.
                if count > 1:
                    warn("Unreachable code detected and eliminated", RuntimeWarning)
                # TODO: add line number and position
                body = _parsed_bf_to_intermediate(bf_body)
                result.append(Loop(body))
    return result


def bf_to_intermediate(bf_code: str) -> AST:
    parsed_bf: bf.AST = bf.parse_bf(bf_code)
    return _parsed_bf_to_intermediate(parsed_bf)
