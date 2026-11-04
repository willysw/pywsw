__all__ = (
    "add_to_global_matrix",
    "add_to_global_vector",
)

import numpy as np  # noqa: F401

from .types import IndexType, Mat, Vec


def add_to_global_matrix(
    idn0: IndexType,
    idn1: IndexType,
    global_k: Mat,
    local_k: Mat,
) -> Mat:
    """Add an matrix associated with an element to a global matrix.

    Parameters
    ----------
    idn0 : int
        Node index at element end 0.
    idn1 : IndexType
        Node index at element end 1.
    global_k : Array2D
        Global matrix to add to.
    local_k : Array2D
        Local matrix to add to `global_v`.

    Returns
    -------
    global_v : Array2D
    """
    DOF: int = local_k.shape[0] // 2
    assert 2 * DOF == local_k.shape[0]  # TODO
    I0, I1 = slice(0, DOF, 1), slice(DOF, 2 * DOF, 1)
    J0, J1 = (
        slice(DOF * idn0, DOF * (idn0 + 1)),
        slice(DOF * idn1, DOF * (idn1 + 1)),
    )
    global_k[J0, J0] += local_k[I0, I0]
    global_k[J0, J1] += local_k[I0, I1]

    global_k[J1, J0] += local_k[I1, I0]
    global_k[J1, J1] += local_k[I1, I1]

    return global_k


def add_to_global_vector(
    n0_tag: IndexType,
    n1_tag: IndexType,
    global_v: Vec,
    local_v: Vec,
) -> Vec:
    """Add a vector associated with an element to a global vector.

    Parameters
    ----------
    idn0 : int
        Node index at element end 0.
    idn1 : IndexType
        Node index at element end 1.
    global_v : Array1D
        Global vector to add to.
    local_v : Array1D
        Local vector to add to `global_v`.

    Returns
    -------
    global_v : Array1D
    """
    DOF: int = local_v.size // 2
    assert 2 * DOF == local_v.size  # TODO
    I0, I1 = slice(0, DOF, 1), slice(DOF, 2 * DOF, 1)
    J0, J1 = (
        slice(DOF * n0_tag, DOF * (n0_tag + 1)),
        slice(DOF * n1_tag, DOF * (n1_tag + 1)),
    )
    global_v[J0] += local_v[I0]
    global_v[J1] += local_v[I1]
    return global_v
