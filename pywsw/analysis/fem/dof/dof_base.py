__all__ = ("DOFBase",)

from abc import abstractmethod
from collections.abc import Iterable, Mapping

import numpy as np

from ..construct import add_to_global_matrix, add_to_global_vector
from ..types import (
    DOFInternals,
    DOFType,
    ElementList,
    IndexType,
    LoadList,
    LoadType,
    Mat,
    MaterialType,
    NodeList,
    SectionType,
    Vec,
)


class DOFBase(DOFType):
    DOF: int = -1

    @classmethod
    @abstractmethod
    def stiffness_matrix(
        cls,
        length: float,
        material: MaterialType,
        section: SectionType,
    ) -> Mat:
        """Compute the element stiffness matrix.

        Parameters
        ----------
        length : float
            Element length
        material : Material
            Element material
        section : Section
            Element section

        Returns
        -------
        K : Array2D
            NxN stiffness matrix where N is 2*DOF.
        """

    @classmethod
    @abstractmethod
    def fixed_end_force_matrix(
        cls,
        length: float,
    ) -> Mat:
        """Compute the element fixed-end force matrix.

        Parameters
        ----------
        length : float
            Element length

        Returns
        -------
        FfeMatrix : Array2D
            NxN matrix of fixed end force coefficients where N is 2*DOF.
        """

    @classmethod
    @abstractmethod
    def fixed_end_force(
        cls,
        length: float,
        loads: Iterable[LoadType],
    ) -> Vec:
        """Compute the element fixed-end force vector.

        Parameters
        ----------
        length : float
            Element length
        loads : Iterable[Load]
            Loads to combine in to the fixed-end forces.

        Returns
        -------
        Ffe : Array1D
            N vector of fixed-end forces where N is 2*DOF.
        """

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
        """Compute internal forces and displacements.

        Parameters
        ----------
        x : float | Iterable[float]
            Locations at which to compute.
        Z : Vec
            Element displacement vector.
        length : float
            Element length.
        loads : Iterable[LoadType]
            Applied loads.
        material : MaterialType
        section : SectionType

        Returns
        -------
        InternalFZ
        """

    """╔══════════════════════════════════════════════════════════╗
       ║                      Common Methods                      ║
       ╚══════════════════════════════════════════════════════════╝"""

    @classmethod
    def get_empty_global_matrix(cls, node_count: int) -> Mat:
        """Return an empty NxN matrix where N is `DOF*node_count`."""
        n = cls.DOF * node_count
        return np.zeros((n, n), dtype=np.float64)

    @classmethod
    def get_empty_global_vector(cls, node_count: int) -> Mat:
        """Return an empty N vector where N is `DOF*node_count`."""
        n = cls.DOF * node_count
        return np.zeros((n,), dtype=np.float64)

    @classmethod
    def get_element_lengths(
        cls,
        elems: ElementList,
        nodes: NodeList,
    ) -> Vec:
        """Compute lengths for each element.

        Parameters
        ----------
        elems : ElementList
        nodes : NodeList

        Returns
        -------
        lengths : Array1D
        """
        return np.fromiter(
            (nodes[_n0].distance(nodes[_n1]) for (_n0, _n1), _ in elems),
            dtype=np.float64,
        )

    @classmethod
    def build_local_stiffness_matrices(
        cls,
        elems: ElementList,
        nodes: NodeList,
        *,
        lengths: Iterable[float] | None = None,
    ) -> tuple[Mat, ...]:
        """Compute stiffness matrices for each element.

        Parameters
        ----------
        elems : Iterable[((n0, n1), Element)]
            Elements and their connectivity. `n0` and `n1` are the indices of the nodes in `nodes`.
        nodes : Iterable[Node]
            Nodes.
        lengths : Iterable[float], optional
            Iterable of lengths. If provided, the lengths will not be recomputed.

        Returns
        -------
        tuple[Array2D, ...]
            A tuple of stiffness matrices for each element.
        """
        if lengths is None:
            lengths: Vec = cls.get_element_lengths(elems, nodes)
        return tuple(
            cls.stiffness_matrix(_l, _elem[1].material, _elem[1].section)
            for _l, _elem in zip(lengths, elems)
        )

    @classmethod
    def build_local_fixed_end_vectors(
        cls,
        elems: ElementList,
        nodes: NodeList,
        loads: LoadList,
        *,
        lengths: Iterable[float] | None = None,
    ) -> tuple[Vec, ...]:
        """Compute fixed-end force vectors for each element.

        Parameters
        ----------
        elems : Iterable[((n0, n1), Element)]
            Elements and their connectivity. `n0` and `n1` are the indices of the nodes in `nodes`.
        nodes : Iterable[Node]
            Nodes.
        loads : Iterable[Iterable[Load]]
            A list of lists of loads. loads[i] will be applied to elems[i].
        lengths : Iterable[float], optional
            Iterable of lengths. If provided, the lengths will not be recomputed.

        Returns
        -------
        tuple[Array1D, ...]
            A tuple of fixed-end force vectors for each element.
        """
        if lengths is None:
            lengths: Vec = cls.get_element_lengths(elems, nodes)
        return tuple(
            cls.fixed_end_force(_l, _loads)
            for _l, _loads in zip(lengths, loads)
        )

    @classmethod
    def build_global_stiffness_matrix(
        cls,
        elems: ElementList,
        nodes: NodeList,
        *,
        elem_matrices: Iterable[Mat] | None = None,
    ) -> Mat:
        """Compute the global stiffness matrix.

        Parameters
        ----------
        elems : Iterable[((n0, n1), Element)]
            Elements and their connectivity. `n0` and `n1` are the indices of the nodes in `nodes`.
        nodes : Iterable[Node]
            Nodes.
        elem_matrices : Iterable[Mat], optional
            If provided, these stiffness matrices will be used instead of recomputed.

        Returns
        -------
        K : Array2D
            Global stiffness matrix.
        """
        if elem_matrices is None:
            elem_matrices: tuple[Mat] = cls.build_local_stiffness_matrices(
                elems, nodes
            )
        global_K: Mat = cls.get_empty_global_matrix(len(nodes))
        for ((_n0, _n1), _), _K in zip(elems, elem_matrices):
            global_K = add_to_global_matrix(_n0, _n1, global_K, _K)
        return global_K

    @classmethod
    def build_global_fixed_end_vector(
        cls,
        elems: ElementList,
        nodes: NodeList,
        loads: LoadList | None = None,
        *,
        fixed_end_vecs: Iterable[Vec] | None = None,
    ) -> Vec:
        """Compute the global fixed-end force vector.

        Parameters
        ----------
        elems : Iterable[((n0, n1), Element)]
            Elements and their connectivity. `n0` and `n1` are the indices of the nodes in `nodes`.
        nodes : Iterable[Node]
            Nodes.
        loads : Iterable[Iterable[Load]]
            A list of lists of loads. loads[i] will be applied to elems[i].
        fixed_end_vecs : Iterable[Vec], optional
            If provided, these vectors will be used instead of recomputing. `loads` will be ignored.

        Returns
        -------
        Ffe : Array1D
            Global fixed-end force vector.
        """
        if fixed_end_vecs is None:
            if loads is None:
                raise ValueError(
                    "Either loads or fixed_end_vecs must be passed."
                )
            fixed_end_vecs = cls.build_local_fixed_end_vectors(
                elems, nodes, loads
            )
        global_Ffe: Vec = cls.get_empty_global_vector(len(nodes))
        for ((_n0, _n1), _), _Ffe in zip(elems, fixed_end_vecs):
            global_Ffe = add_to_global_vector(_n0, _n1, global_Ffe, _Ffe)
        return global_Ffe

    @classmethod
    def build_global_unknown_vectors(
        cls,
        nodes: NodeList,
        supports: Mapping[IndexType, Iterable[float]],
    ) -> tuple[Vec, Vec]:
        """Build unknown vectors for the solver.

        This builds vectors where unknowns are NaN and knowns are 0.0. These
        are used during solving to partition the matrices and vectors.

        Parameters
        ----------
        nodes : Iterable[Node]
            Nodes.
        supports : Mapping[int, Iterable[float]]
            A dictionary where the key is the index of a Node in nodes, and the Iterable of floats is the support condition.

        Returns
        -------
        R, Z : (Array1D, Array1D)
            Unkown reaction and displacement vectors.
        """
        num_nodes = len(nodes)
        R: Vec = cls.get_empty_global_vector(num_nodes)
        for _i, _vec in supports.items():
            if _i < num_nodes:
                J0: slice = slice(cls.DOF * _i, cls.DOF * (_i + 1), 1)
                R[J0] += _vec
        return np.where(R, np.nan, 0), np.where(R, 0, np.nan)
