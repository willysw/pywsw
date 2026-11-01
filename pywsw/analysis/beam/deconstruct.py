__all__ = (
    "get_local_element_vector",
    "get_local_element_vectors",
    "get_local_vector",
    "get_local_vectors",
)

from collections.abc import Iterable

import numpy as np

from .types import Mat, TagType, Vec


def get_local_vector(global_v: Vec, n: TagType, DOF: int) -> Vec:
    J = slice(DOF * n, DOF * (n + 1), 1)
    return global_v[J]


def get_local_vectors(global_v: Vec, ns: Iterable[TagType], DOF: int) -> Mat:
    return np.array([get_local_vector(global_v, ni, DOF) for ni in ns])


def get_local_element_vector(
    global_v: Vec, n0: TagType, n1: TagType, DOF: int
) -> Vec:
    vecs: Mat = get_local_vectors(global_v, (n0, n1), DOF)
    return np.concat((vecs[0, :], vecs[1, :]))


def get_local_element_vectors(
    global_v, ns01: Iterable[Iterable[int, int]], DOF: int
) -> Mat:
    return np.array(
        [get_local_element_vector(global_v, n0i, n1i, DOF) for n0i, n1i in ns01]
    )
