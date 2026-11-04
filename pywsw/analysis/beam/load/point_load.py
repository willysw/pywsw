__all__ = ("PointLoad",)
from dataclasses import KW_ONLY, dataclass
from typing import ClassVar

import numpy as np

from ..types import Vec
from .load_base import LoadBase


@dataclass(frozen=True)
class PointLoad(LoadBase):
    load: float
    _: KW_ONLY
    HEAVISIDE_0: ClassVar[float] = 0.5

    def w_fn(self, x: Vec) -> Vec:
        return np.zeros_like(x)

    def omega_fn(self, x: Vec, n: int) -> Vec:
        return (
            self.load
            * np.heaviside(x - self.offset, self.HEAVISIDE_0)
            * (self.offset**n)
        )
