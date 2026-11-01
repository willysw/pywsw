from abc import ABC, abstractmethod
from collections.abc import Iterable

from ..types import LoadType, Mat, Vec


class DOFBase(ABC):
    DOF: int = -1

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
    def fixed_end_force(cls, load: float, loads: Iterable[LoadType]) -> Vec: ...
