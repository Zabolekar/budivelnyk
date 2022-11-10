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

class Increment(Command):
    """ Increment current cell's value. """
    def __repr__(self) -> str:
        return 'Increment'

class Decrement(Command):
    """ Decrement current cell's value. """
    def __repr__(self) -> str:
        return 'Decrement'

class MoveForward(Command):
    """ Increment cell pointer. """
    def __repr__(self) -> str:
        return 'MoveForward'

class MoveBack(Command):
    """ Decrement cell pointer. """
    def __repr__(self) -> str:
        return 'MoveBack'

class Output(Command):
    """ Output current cell's value. """
    def __repr__(self) -> str:
        return 'Output'

class Input(Command):
    """ Store input value in current cell. """
    def __repr__(self) -> str:
        return 'Input'

@dataclass
class Cycle(Node):
    """ While current cell's value is non-zero, repeat cycle's body. """
    body: list[Node]
    
    def __repr__(self) -> str:
        return f'Cycle{self.body}'


# Optimization commands

@dataclass
class AddConstant(Command):
    """ Add constant to current cell's value. """
    constant: int
    
    def __repr__(self) -> str:
        return f'AddConstant({self.constant})'

@dataclass
class MoveByConstant(Command):
    """ Add constant to cell pointer. """
    constant: int
    
    def __repr__(self) -> str:
        return f'MoveByConstant({self.constant})'


# Optimizations

Optimization = Callable[[list[Node]], list[Node]]

def same_command_sequence_optimization(intermediate: list[Node]) -> list[Node]:
    result: list[Node] = []
    for (_, g) in groupby(intermediate, lambda node: type(node)):
        group = list(g)
        count = len(group)
        match group[0]:
            case Increment() if count > 1:
                result.append(AddConstant(count))
            case Decrement() if count > 1:
                result.append(AddConstant(-count))
            case MoveForward() if count > 1:
                result.append(MoveByConstant(count))
            case MoveBack() if count > 1:
                result.append(MoveByConstant(-count))
            case Cycle(body):
                optimized_body = same_command_sequence_optimization(body)
                result.append(Cycle(optimized_body))
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
                yield Cycle(list(body))
            case ']':
                if expect_closing_bracket:
                    break
                else:
                    raise RuntimeError('Unexpected closing bracket')
                    # TODO: add line number and position
    else:
        if expect_closing_bracket:
            raise RuntimeError('Closing bracket expected') 
