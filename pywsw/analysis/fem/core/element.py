from dataclasses import KW_ONLY, dataclass, field
from functools import cached_property

from ..types import ElementType, TagType
from .material import Material
from .section import Section


@dataclass(frozen=True)
class Element(ElementType):
    node0: TagType
    node1: TagType
    _: KW_ONLY
    material: Material = field(default_factory=Material, repr=False)
    section: Section = field(default_factory=Section, repr=False)

    @cached_property
    def EI(self) -> float:
        return self.material.E_b * self.section.I_b

    @cached_property
    def EA(self) -> float:
        return self.material.E_a * self.section.A

    @cached_property
    def nodes(self) -> tuple[TagType, TagType]:
        return self.node0, self.node1
