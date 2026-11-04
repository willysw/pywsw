__all__ = ("LoadBase",)

from abc import abstractmethod
from dataclasses import KW_ONLY, dataclass, field

import numpy as np

from ..types import LoadType, Vec


@dataclass(frozen=True)
class LoadBase(LoadType):
    _: KW_ONLY
    offset: float = 0.0
    x_start: float = field(default=0.0, repr=False)
    x_end: float = field(default=np.inf, repr=False)

    """ ABSTRACT METHODS """

    @abstractmethod
    def w_fn(self, x: Vec) -> Vec: ...

    @abstractmethod
    def omega_fn(self, x: Vec, n: int) -> Vec: ...

    """ CLASS METHODS """

    def __call__(self, x):
        return self._return(self.omega(x, 0))

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
    def _return(val: Vec) -> float | Vec:
        if val.size == 1:
            return val.item()
        else:
            return val
