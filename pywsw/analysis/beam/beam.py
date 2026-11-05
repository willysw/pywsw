from collections import defaultdict
from collections.abc import Iterable
from functools import cached_property
from typing import ClassVar, NamedTuple

import matplotlib.pyplot as plt
import numpy as np

from pywsw.analysis.fem import (
    Element,
    Material,
    Node,
    Section,
    get_local_element_vectors,
    solve_system,
)
from pywsw.analysis.fem.dof import BeamDOF
from pywsw.analysis.fem.types import IndexType, LoadType, Mat, Vec

type SupportCondType = tuple[float, float]


class BeamResult(NamedTuple):
    X: Vec
    V: Vec
    M: Vec
    U: Vec
    Phi: Vec
    x_rxn: Vec
    V_rxn: Vec
    M_rxn: Vec
    U_node: Vec
    Phi_node: Vec

    def plot(self) -> tuple[plt.Figure, tuple[tuple[plt.Axes, ...], ...]]:
        fig, axs = plt.subplots(2, 2)
        for _ax_row in axs:
            for _ax in _ax_row:
                _ax.grid(True, which="both")
                _ax.axhline(0.0, color="black")
                for _x in self.x_rxn:
                    _ax.axvline(_x, color="black")

        axs[0][0].plot(self.X, self.V)
        axs[1][0].plot(self.X, self.M)
        axs[0][1].plot(self.X, self.U)
        axs[1][1].plot(self.X, self.Phi)

        return fig, axs


class Beam:
    node_loc: Vec
    length: Vec
    E: Vec
    I: Vec
    supports: Mat

    elems: tuple[Element]
    nodes: tuple[Node]

    FREE: ClassVar[SupportCondType] = (0.0, 0.0)
    PIN: ClassVar[SupportCondType] = (1.0, 0.0)
    FIX: ClassVar[SupportCondType] = (1.0, 0.0)

    def __init__(
        self,
        spans: float | Iterable[float],
        supports: SupportCondType | Iterable[SupportCondType] = (1.0, 0.0),
        modulus: float | Iterable[float] = 1.0,
        inertia: float | Iterable[float] = 1.0,
    ) -> None:
        self.length = np.atleast_1d(np.asarray(spans))
        span_count = self.length.size
        self.node_loc = np.concat(((0.0,), np.cumsum(self.length)))

        self.E = np.atleast_1d(np.asarray(modulus, dtype=np.float64))
        if self.E.size != span_count:
            self.E = np.full_like(self.length, self.E[0], dtype=np.float64)

        self.I = np.atleast_1d(np.asarray(inertia, dtype=np.float64))
        if self.I.size != span_count:
            self.I = np.full_like(self.length, self.I[0], dtype=np.float64)

        self.supports = np.atleast_2d(np.asarray(supports, dtype=np.float64))
        if self.supports.shape[0] != span_count + 1:
            self.supports = np.full(
                (span_count + 1, 2), self.supports[0], dtype=np.float64
            )

        self.elems = tuple(
            Element(
                _i,
                _i + 1,
                material=Material(E_b=self.E[_i]),
                section=Section(I_b=self.I[_i]),
            )
            for _i in range(span_count)
        )

        self.nodes = tuple(
            Node(x=self.node_loc[_i]) for _i in range(span_count + 1)
        )

    @cached_property
    def local_K(self) -> tuple[Mat]:
        """Tuple of span local stifness matrices."""
        return BeamDOF.build_local_stiffness_matrices(
            elems=self._elem_list,
            nodes=self.nodes,
            lengths=self.length,
        )

    @cached_property
    def global_K(self) -> Mat:
        """Global stiffness matrix."""
        return BeamDOF.build_global_stiffness_matrix(
            elems=self._elem_list,
            nodes=self.nodes,
            elem_matrices=self.local_K,
        )

    @cached_property
    def unknowns(self) -> tuple[Vec, Vec]:
        """Unknown reaction and displacement vectors.

        Returns
        -------
        Ro, Zo : (Vec, Vec)
        """
        return BeamDOF.build_global_unknown_vectors(
            nodes=self.nodes,
            supports={_i: _supp for _i, _supp in enumerate(self.supports)},
        )

    def __call__(
        self,
        load: LoadType | Iterable[tuple[LoadType, Iterable[IndexType]]],
        *,
        interval_size: float = 0.0,
        n_intervals: int = 100,
    ) -> BeamResult:
        load_list = self._parse_loads(load)
        global_K: Mat = self.global_K
        local_Ffe: tuple[Vec] = BeamDOF.build_local_fixed_end_vectors(
            elems=self._elem_list,
            nodes=self.nodes,
            loads=load_list,
            lengths=self.length,
        )
        global_Ffe = BeamDOF.build_global_fixed_end_vector(
            elems=self._elem_list,
            nodes=self.nodes,
            fixed_end_vecs=local_Ffe,
        )
        Ro, Zo = self.unknowns

        sol: tuple[Vec, Vec] = solve_system(
            K=global_K, z=Zo, f=global_Ffe, r=Ro
        )

        elem_Z: Mat = get_local_element_vectors(
            sol[1],
            [(_i, _i + 1) for _i in range(len(self.length))],
            BeamDOF.DOF,
        )

        X: Vec = self._build_X_vectors(interval_size, n_intervals)
        internals = [
            BeamDOF.compute_internals(
                _x,
                _z,
                length=_l,
                loads=_load,
                material=_elem.material,
                section=_elem.section,
            )
            for _x, _l, _z, _load, _elem in zip(
                X, self.length, elem_Z, load_list, self.elems
            )
        ]

        return BeamResult(
            X=np.concat([_x + _x0 for _x, _x0 in zip(X, self.node_loc)]),
            V=np.concat([_int.Fx[0] for _int in internals]),
            M=np.concat([_int.Fx[1] for _int in internals]),
            U=np.concat([_int.Zx[0] for _int in internals]),
            Phi=np.concat([_int.Zx[1] for _int in internals]),
            x_rxn=self.node_loc,
            V_rxn=sol[0][0:-2:2],
            M_rxn=sol[0][1:-1:2],
            U_node=sol[1][0:-2:2],
            Phi_node=sol[1][1:-1:2],
        )

    @cached_property
    def _elem_list(
        self,
    ) -> list[tuple[tuple[IndexType, IndexType], Element]]:
        return [((_i, _i + 1), _elem) for _i, _elem in enumerate(self.elems)]

    def _build_X_vectors(
        self,
        interval_size: float = 0.0,
        n_intervals: int = 100,
    ) -> Vec:
        if interval_size:
            return [
                np.linspace(0.0, _l, _l // interval_size) for _l in self.length
            ]
        else:
            return [np.linspace(0.0, _l, n_intervals) for _l in self.length]

    def _parse_loads(
        self,
        load: LoadType | Iterable[tuple[LoadType, Iterable[IndexType]]],
    ) -> list[tuple[LoadType]]:
        if isinstance(load, LoadType):
            loads = [(load,) for _ in self.length]
        else:
            rmap: dict[int, set[int]] = defaultdict(set)
            for _load, _apply_to in load:
                for _elem_id in _apply_to:
                    rmap[_elem_id].add(_load)
            loads: list[tuple[LoadType, ...]] = [
                tuple(rmap[_i]) for _i in range(len(self.length))
            ]
        return loads
