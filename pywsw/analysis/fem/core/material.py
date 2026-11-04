from dataclasses import dataclass

from ..types import MaterialType


@dataclass(frozen=True)
class Material(MaterialType):
    E_a: float = 1.0
    E_b: float = 1.0
    E_v: float = 1.0
