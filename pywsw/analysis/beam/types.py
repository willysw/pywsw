from collections.abc import Iterable
from typing import NamedTuple, Protocol, abstractmethod, overload

import numpy as np
from numpy.typing import ArrayLike, NDArray

TagType = type[int]

IDs = type[np.ndarray[tuple[int], TagType]]
Vec = type[np.ndarray[tuple[int], float]]
Mat = type[np.ndarray[tuple[int, int], float]]
Arr = type[NDArray[float]]


class Node(NamedTuple):
    x: float
    fixity: tuple[float, float] = (0.0, 0.0)

    def distance(self, other_node: "Node") -> float:
        return abs(self.x - other_node.x)


class Element(NamedTuple):
    node0: TagType
    node1: TagType
    EI: float = 1.0


class LoadType(Protocol):
    offset: float
    x_start: float
    x_end: float

    """ ABSTRACT METHODS """

    @abstractmethod
    def w_fn(self, x: NDArray[float]) -> NDArray[float]: ...

    @abstractmethod
    def omega_fn(self, x: NDArray[float], n: int) -> NDArray[float]: ...

    """ CLASS METHODS """

    @overload
    def __call__(self, x: float) -> float: ...
    @overload
    def __call__(self, x: NDArray[float]) -> NDArray[float]: ...
    @overload
    def __call__(self, x: Iterable[float]) -> NDArray[float]: ...
    @abstractmethod
    def __call__(self, x): ...

    @overload
    def w(self, x: float) -> float: ...
    @overload
    def w(self, x: NDArray[float]) -> NDArray[float]: ...
    @overload
    def w(self, x: Iterable[float]) -> NDArray[float]: ...
    @abstractmethod
    def w(self, x): ...

    @overload
    def omega(self, x: float, n: int) -> float: ...
    @overload
    def omega(self, x: NDArray[float], n: int) -> NDArray[float]: ...
    @overload
    def omega(self, x: Iterable[float], n: int) -> NDArray[float]: ...
    @abstractmethod
    def omega(self, x, n): ...


class DOFType(Protocol):
    DOF: int

    @classmethod
    @abstractmethod
    def stiffness_matrix(
        cls,
        length: float,
        *,
        E_a: float = 1.0,
        E_b: float = 1.0,
        E_v: float = 1.0,
        A_a: float = 1.0,
        A_v: float = 1.0,
        I_b: float = 1.0,
    ) -> Mat: ...

    @classmethod
    @abstractmethod
    def fixed_end_force_matrix(cls, length: float) -> Mat: ...

    @classmethod
    @abstractmethod
    def fixed_end_force(
        cls, length: float, loads: Iterable[LoadType]
    ) -> Vec: ...


__all__ = (
    "Arr",
    "ArrayLike",
    "Element",
    "IDs",
    "LoadType",
    "Mat",
    "Node",
    "TagType",
    "Vec",
)
