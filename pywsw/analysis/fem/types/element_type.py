__all__ = ("ElementType", "MaterialType", "SectionType")

from typing import Protocol, abstractmethod, runtime_checkable

from .fem_alias import TagType


@runtime_checkable
class MaterialType(Protocol):
    E_a: float
    E_b: float
    E_v: float


@runtime_checkable
class SectionType(Protocol):
    A: float
    I_b: float
    A_v: float


@runtime_checkable
class ElementType(Protocol):
    node0: TagType
    node1: TagType
    material: MaterialType
    section: SectionType

    @property
    @abstractmethod
    def EI(self) -> float: ...

    @property
    @abstractmethod
    def EA(self) -> float: ...

    @property
    @abstractmethod
    def nodes(self) -> tuple[TagType, TagType]: ...
