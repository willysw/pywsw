from collections.abc import Hashable, Iterable, Mapping
from typing import Any, Protocol, abstractmethod, overload, runtime_checkable

import numpy as np
from numpy.typing import ArrayLike

type TagType = Hashable
type IndexType = int

type IDs = np.ndarray[tuple[int], IndexType]
type Vec = np.ndarray[tuple[int], float]
type Mat = np.ndarray[tuple[int, int], float]
type Arr = np.ndarray[tuple[Any], float]


@runtime_checkable
class NodeType(Protocol):
    x: float = 0.0
    y: float = 0.0

    @abstractmethod
    def distance(self, other_node: "NodeType") -> float: ...


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


@runtime_checkable
class LoadType(Protocol):
    offset: float
    x_start: float
    x_end: float

    @overload
    def __call__(self, x: float) -> float: ...
    @overload
    def __call__(self, x: Vec) -> Vec: ...
    @overload
    def __call__(self, x: Iterable[float]) -> Vec: ...
    @abstractmethod
    def __call__(self, x): ...

    @overload
    def w(self, x: float) -> float: ...
    @overload
    def w(self, x: Vec) -> Vec: ...
    @overload
    def w(self, x: Iterable[float]) -> Vec: ...
    @abstractmethod
    def w(self, x): ...

    @overload
    def omega(self, x: float, n: int) -> float: ...
    @overload
    def omega(self, x: Vec, n: int) -> Vec: ...
    @overload
    def omega(self, x: Iterable[float], n: int) -> Vec: ...
    @abstractmethod
    def omega(self, x, n): ...


type IndexPairType = tuple[IndexType, IndexType]
type ElementList = Iterable[tuple[IndexPairType, ElementType]]
type NodeList = Iterable[NodeType]
type LoadList = Iterable[Iterable[LoadType]]


@runtime_checkable
class DOFType(Protocol):
    DOF: int

    @classmethod
    @abstractmethod
    def stiffness_matrix(
        cls,
        length: float,
        material: MaterialType,
        section: SectionType,
    ) -> Mat: ...

    @classmethod
    @abstractmethod
    def fixed_end_force_matrix(
        cls,
        length: float,
    ) -> Mat: ...

    @classmethod
    @abstractmethod
    def fixed_end_force(
        cls,
        length: float,
        loads: Iterable[LoadType],
    ) -> Vec: ...

    """╔══════════════════════════════════════════════════════════╗
       ║                      Common Methods                      ║
       ╚══════════════════════════════════════════════════════════╝"""

    @classmethod
    def get_empty_global_matrix(cls, node_count: int) -> Mat: ...

    @classmethod
    def get_empty_global_vector(cls, node_count: int) -> Mat: ...

    @classmethod
    def get_element_lengths(
        cls, elems: ElementList, nodes: NodeList
    ) -> Vec: ...

    @classmethod
    def build_local_stiffness_matrices(
        cls,
        elems: ElementList,
        nodes: NodeList,
        *,
        lengths: Iterable[float] | None = None,
    ) -> tuple[Mat, ...]: ...

    @classmethod
    def build_local_fixed_end_vectors(
        cls,
        elems: ElementList,
        nodes: NodeList,
        loads: LoadList,
        *,
        lengths: Iterable[float] | None = None,
    ) -> tuple[Vec, ...]: ...

    @overload
    @classmethod
    def build_global_stiffness_matrix(
        cls, elems: ElementList, nodes: NodeList
    ) -> Mat: ...
    @overload
    @classmethod
    def build_global_stiffness_matrix(
        cls,
        elems: ElementList,
        nodes: NodeList,
        *,
        elem_matrices: Iterable[Mat],
    ) -> Mat: ...

    @overload
    @classmethod
    def build_global_fixed_end_vector(
        cls,
        elems: ElementList,
        nodes: NodeList,
        loads: LoadList,
    ) -> Vec: ...
    @overload
    @classmethod
    def build_global_fixed_end_vector(
        cls,
        elems: ElementList,
        nodes: NodeList,
        *,
        fixed_end_vecs: Iterable[Vec],
    ) -> Vec: ...

    @classmethod
    def build_global_unknown_vectors(
        cls, nodes: NodeList, supports: Mapping[IndexType, Vec]
    ) -> tuple[Vec, Vec]: ...


__all__ = (
    "Arr",
    "ArrayLike",
    "ElementList",
    "ElementType",
    "IDs",
    "IndexPairType",
    "LoadList",
    "LoadType",
    "Mat",
    "MaterialType",
    "NodeList",
    "NodeType",
    "SectionType",
    "TagType",
    "Vec",
)
