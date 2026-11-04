__all__ = ("UniformLoad",)

from dataclasses import dataclass

import numpy as np

from ..types import Vec
from .load_base import LoadBase


@dataclass(frozen=True)
class UniformLoad(LoadBase):
    load: float

    def w_fn(self, x: Vec) -> Vec:
        return np.full_like(x, self.load)

    def omega_fn(self, x: Vec, n: int) -> Vec:
        return self.load * (x ** (n + 1)) / (n + 1)
