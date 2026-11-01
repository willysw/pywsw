__all__ = ("LoadBase",)

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass, field
from typing import overload

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class LoadBase(ABC):
    _: KW_ONLY
    offset: float = 0.0
    x_start: float = field(default=0.0, repr=False)
    x_end: float = field(default=np.inf, repr=False)

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
    def __call__(self, x):
        return self._return(self.omega(x, 0))

    @overload
    def w(self, x: float) -> float: ...
    @overload
    def w(self, x: NDArray[float]) -> NDArray[float]: ...
    @overload
    def w(self, x: Iterable[float]) -> NDArray[float]: ...
    def w(self, x):
        x = np.asarray(x, dtype=np.float64)
        x_max = x.max()
        w = self.w_fn(x)

        # Apply interval if interval exists.
        if self.x_start > 0:
            x0 = max(self.x_start, 0.0)
            w = np.where(x < x0, 0.0, w)

        if self.x_end < x_max:
            x1 = min(self.x_end, x_max)
            w = np.where(x > x1, 0.0, w)

        return self._return(w)

    @overload
    def omega(self, x: float, n: int) -> float: ...
    @overload
    def omega(self, x: NDArray[float], n: int) -> NDArray[float]: ...
    @overload
    def omega(self, x: Iterable[float], n: int) -> NDArray[float]: ...
    def omega(self, x, n):
        x = np.asarray(x, dtype=np.float64)
        x_max = x.max()
        omega = self.omega_fn(x, n)

        # Window method if interval exists.
        if self.x_start > 0 or self.x_end < x_max:
            x0 = max(self.x_start, 0.0)
            omega_0 = self.omega_fn(x0, n)
            omega = np.where(x < x0, 0.0, omega - omega_0)

            x1 = min(self.x_end, x_max)
            omega_1 = self.omega_fn(x1, n)
            omega = np.where(x > x1, omega_1 - omega_0, omega)

        return self._return(omega)

    """ STATIC METHODS """

    @staticmethod
    def _return(val: NDArray[float]) -> float | NDArray[float]:
        if val.size == 1:
            return val.item()
        else:
            return val
