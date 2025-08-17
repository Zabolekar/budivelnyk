from abc import ABC, abstractmethod
from ..intermediate import AST

class Frontend(ABC):
    @staticmethod
    @abstractmethod
    def to_intermediate(code: str) -> AST:
        ...
