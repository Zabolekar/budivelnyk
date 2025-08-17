from typing import TypeAlias
from dataclasses import dataclass

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
