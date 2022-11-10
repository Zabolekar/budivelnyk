from typing import Iterable, Callable
from dataclasses import dataclass
from itertools import groupby


# Abstract base classes

class Node:
    """ Abstract syntax tree node. """
    pass

class Command(Node):
    """ Any leaf node. """
    pass


# BF commands

@dataclass
class Increment(Command):
    """ Increment current cell's value. """
    pass

@dataclass
class Decrement(Command):
    """ Decrement current cell's value. """
    pass

@dataclass
class MoveForward(Command):
    """ Increment cell pointer. """
    pass

@dataclass
class MoveBack(Command):
    """ Decrement cell pointer. """
    pass

@dataclass
class Output(Command):
    """ Output current cell's value. """
    pass

@dataclass
class Input(Command):
    """ Store input value in current cell. """
    pass

@dataclass
class Loop(Node):
    """ While current cell's value is non-zero, repeat loop's body. """
    body: list[Node]


# Optimization commands

@dataclass
class Add(Command):
    """ Add constant to current cell's value. """
    constant: int

@dataclass
class Subtract(Command):
    """ Subtract constant from current cell's value. """
    constant: int

@dataclass
class MoveForwardBy(Command):
    """ Add constant to cell pointer. """
    constant: int

@dataclass
class MoveBackBy(Command):
    """ Subtract constant from cell pointer. """
    constant: int

@dataclass
class MultipleOutput(Command):
    """ Output current cell's value multiple times. """
    count: int

@dataclass
class MultipleInput(Command):
    """ Get multiple input values and store the last one in current cell. """
    count: int


# Optimizations

Optimization = Callable[[list[Node]], list[Node]]

def same_command_sequence_optimization(intermediate: list[Node]) -> list[Node]:
    result: list[Node] = []
    for (_, g) in groupby(intermediate, lambda node: type(node)):
        group = list(g)
        count = len(group)
        match group[0]:
            case Increment() if count > 1:
                result.append(Add(count))
            case Decrement() if count > 1:
                result.append(Subtract(count))
            case MoveForward() if count > 1:
                result.append(MoveForwardBy(count))
            case MoveBack() if count > 1:
                result.append(MoveBackBy(count))
            case Output() if count > 1:
                result.append(MultipleOutput(count))
            case Input() if count > 1:
                result.append(MultipleInput(count))
            case Loop(body):
                optimized_body = same_command_sequence_optimization(body)
                result.append(Loop(optimized_body))
            case _:
                result.extend(group)
    return result

default_optimizations = [same_command_sequence_optimization]


# Parsing BF code

def bf_to_intermediate(bf_code: str, optimizations: list[Optimization]|None=None) -> list[Node]:
    sequence = iter(bf_code)
    intermediate = list(_bf_sequence_to_intermediate(sequence, expect_closing_bracket=False))
    for optimization in optimizations or default_optimizations:
        intermediate = optimization(intermediate)
    return intermediate


def _bf_sequence_to_intermediate(sequence: Iterable[str], expect_closing_bracket: bool) -> Iterable[Node]:
    for char in sequence:
        match char:
            case '+': yield Increment()
            case '-': yield Decrement()
            case '>': yield MoveForward()
            case '<': yield MoveBack()
            case '.': yield Output()
            case ',': yield Input()
            case '[':
                body = _bf_sequence_to_intermediate(sequence, expect_closing_bracket=True)
                yield Loop(list(body))
            case ']':
                if expect_closing_bracket:
                    break
                else:
                    raise RuntimeError('Unexpected closing bracket')
                    # TODO: add line number and position
    else:
        if expect_closing_bracket:
            raise RuntimeError('Closing bracket expected') 
