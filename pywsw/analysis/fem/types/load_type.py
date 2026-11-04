__all__ = ("LoadType",)

from collections.abc import Iterable
from typing import (
    Protocol,
    abstractmethod,
    overload,
    runtime_checkable,
)

from .fem_alias import Vec


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
