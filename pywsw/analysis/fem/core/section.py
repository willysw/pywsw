from dataclasses import dataclass

from ..types import SectionType


@dataclass(frozen=True)
class Section(SectionType):
    A: float = 1.0
    I_b: float = 1.0
    A_v: float = 1.0
