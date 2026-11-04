__all__ = ("GenericLoad",)

from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, field

import numpy as np
from scipy.integrate import cumulative_simpson, quad

from ..types import Vec
from .load_base import LoadBase

LoadFuncType = Callable[[Vec], Vec]


@dataclass(frozen=True)
class GenericLoad(LoadBase):
    _: KW_ONLY
    load_func: LoadFuncType | None = field(default=None, repr=False)

    def w_fn(self, x: Vec) -> Vec:
        if self.load_func is None:
            return np.full_like(x, 0.0)
        else:
            return self._return(self.load_func(x - self.offset))

    def omega_fn(self, x: Vec, n: int) -> Vec:
        if self.load_func is None:
            return np.zeros_like(x)

        if x.size == 1:
            return quad(lambda X: (X**n) * (self.w(X).item()), 0, x.item())[0]
        else:
            return cumulative_simpson(y=(x**n) * self.w(x), x=x, initial=0.0)
