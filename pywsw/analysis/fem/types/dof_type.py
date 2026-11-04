__all__ = (
    "DOFInternals",
    "DOFType",
    "ElementList",
    "IndexPairType",
    "LoadList",
    "NodeList",
)

from collections.abc import Iterable, Mapping
from typing import (
    NamedTuple,
    Protocol,
    abstractmethod,
    overload,
    runtime_checkable,
)

from .element_type import ElementType, MaterialType, SectionType
from .fem_alias import IndexType, Mat, Vec
from .load_type import LoadType
from .node_type import NodeType

type IndexPairType = tuple[IndexType, IndexType]
type ElementList = Iterable[tuple[IndexPairType, ElementType]]
type NodeList = Iterable[NodeType]
type LoadList = Iterable[Iterable[LoadType]]


class DOFInternals(NamedTuple):
    Fx: Mat
    Zx: Mat
    F0: Vec
    Z0: Vec
    F1: Vec
    Z1: Vec
    Omega: Mat


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

    @classmethod
    @abstractmethod
    def compute_internals(
        cls,
        x: float | Iterable[float],
        Z: Vec,
        *,
        length: float,
        loads: Iterable[LoadType],
        material: MaterialType,
        section: SectionType,
    ) -> DOFInternals: ...

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
        cls, nodes: NodeList, supports: Mapping[IndexType, Iterable[float]]
    ) -> tuple[Vec, Vec]: ...
