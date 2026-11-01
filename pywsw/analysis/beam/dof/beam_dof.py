from collections.abc import Iterable

import numpy as np

from ..types import LoadType, Mat, Vec
from .dof_base import DOFBase


class BeamDOF(DOFBase):
    DOF: int = 2

    @classmethod
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
    ) -> Mat:
        L, L2, L3 = length, length**2, length**3
        return (
            E_b
            * I_b
            * np.array(
                [
                    [-12 / L3, -6 / L2, 12 / L3, -6 / L2],
                    [6 / L2, 4 / L, -6 / L2, 2 / L],
                    [12 / L3, 6 / L2, -12 / L3, 6 / L2],
                    [6 / L2, 2 / L, -6 / L2, 4 / L],
                ]
            )
        )

    @classmethod
    def fixed_end_force_matrix(cls, length: float) -> Mat:
        L, L2, L3 = length, length**2, length**3
        return np.array(
            [
                [1, 0, -3 / L2, 2 / L3],
                [0, -1, 2 / L, -1 / L2],
                [0, 0, 3 / L2, -2 / L3],
                [0, 0, 1 / L, -1 / L2],
            ]
        )

    @classmethod
    def fixed_end_force(cls, length: float, loads: Iterable[LoadType]) -> Vec:
        a: Mat = cls.fixed_end_force_matrix(length)
        w: Vec = np.zeros((2 * cls.DOF,), dtype=np.float64)
        for load in loads:
            w += np.asarray([load.omega(length, n) for n in range(2 * cls.DOF)])
        return np.linalg.matmul(a, w)
