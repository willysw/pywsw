__all__ = ("PointLoad",)
from dataclasses import KW_ONLY, dataclass
from typing import ClassVar

import numpy as np
from numpy.typing import NDArray

from .load_base import LoadBase


@dataclass(frozen=True)
class PointLoad(LoadBase):
    load: float
    _: KW_ONLY
    HEAVISIDE_0: ClassVar[float] = 0.5

    def w_fn(self, x: NDArray[float]) -> NDArray[float]:
        return np.zeros_like(x)

    def omega_fn(self, x: NDArray[float], n: int) -> NDArray[float]:
        return (
            self.load
            * np.heaviside(x - self.offset, self.HEAVISIDE_0)
            * (self.offset**n)
        )
