__all__ = ("UniformLoad",)

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .load_base import LoadBase


@dataclass
class UniformLoad(LoadBase):
    load: float

    def w_fn(self, x: NDArray[float]) -> NDArray[float]:
        return np.full_like(x, self.load)

    def omega_fn(self, x: NDArray[float], n: int) -> NDArray[float]:
        return self.load * (x ** (n + 1)) / (n + 1)
