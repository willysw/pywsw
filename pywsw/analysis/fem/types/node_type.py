__all__ = ("NodeType",)

from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class NodeType(Protocol):
    x: float = 0.0
    y: float = 0.0

    @abstractmethod
    def distance(self, other_node: "NodeType") -> float: ...
