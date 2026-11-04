from dataclasses import dataclass
from math import sqrt

from ..types import NodeType


@dataclass(frozen=True)
class Node(NodeType):
    x: float = 0.0
    y: float = 0.0

    def distance(self, other_node: "Node") -> float:
        return sqrt((self.x - other_node.x) ** 2 + (self.y - other_node.y) ** 2)
