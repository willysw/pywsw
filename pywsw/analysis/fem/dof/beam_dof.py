__all__ = ("BeamDOF",)

from collections.abc import Iterable

import numpy as np

from ..types import (
    DOFInternals,
    LoadType,
    Mat,
    MaterialType,
    SectionType,
    Vec,
)
from .dof_base import DOFBase

_GLOBAL_TO_LOCAL = np.diagflat((-1, -1, 1, 1))


class BeamDOF(DOFBase):
    DOF: int = 2

    @classmethod
    def stiffness_matrix(
        cls,
        length: float,
        material: MaterialType,
        section: SectionType,
    ) -> Mat:
        L, L2, L3 = length, length**2, length**3
        return (
            material.E_b
            * section.I_b
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

    @classmethod
    def compute_internals(
        cls,
        x: float | Iterable[float],
        Z: Vec,
        *,
        length: float,
        loads: Iterable[LoadType],
        material: MaterialType,
        section: SectionType,
    ) -> DOFInternals:
        X = np.atleast_1d(x)
        K: Mat = cls.stiffness_matrix(length, material, section)
        Ffe: Vec = cls.fixed_end_force(length, loads)

        # Compute End Reactions
        F: Vec = np.matmul(_GLOBAL_TO_LOCAL, np.matmul(K, Z) + Ffe)

        # Compute Omega vectors
        OM: list[Vec] = [
            np.sum([_load.omega(X, _n) for _load in loads], axis=0)
            for _n in (0, 1, 2, 3)
        ]

        EI = material.E_b * section.I_b
        X_2, X_3 = X**2, X**3
        V: Vec = F[0] + OM[0]
        M: Vec = F[1] + V * X - OM[1]
        Q: Vec = Z[1] + M * X / EI - V * X_2 / (2 * EI) + OM[2] / (2 * EI)
        U: Vec = (
            Z[0]
            + Q * X
            - M * X_2 / (2 * EI)
            + V * X_3 / (6 * EI)
            - OM[3] / (6 * EI)
        )

        return DOFInternals(
            Fx=np.asarray((V, M)),
            Zx=np.asarray((U, Q)),
            F0=F[0:2],
            Z0=Z[0:2],
            F1=F[2:4],
            Z1=Z[2:4],
            Omega=np.asarray(OM),
        )
