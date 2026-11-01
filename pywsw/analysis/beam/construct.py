__all__ = (
    "add_to_global_matrix",
    "add_to_global_vector",
)

from .types import Mat, TagType, Vec


def add_to_global_matrix(
    n0_tag: TagType,
    n1_tag: TagType,
    global_k: Mat,
    local_k: Mat,
) -> Mat:
    DOF: int = local_k.shape[0] // 2
    assert 2 * DOF == local_k.shape[0]  # TODO
    I0, I1 = slice(0, DOF, 1), slice(DOF, 2 * DOF, 1)
    J0, J1 = (
        slice(DOF * n0_tag, DOF * (n0_tag + 1)),
        slice(DOF * n1_tag, DOF * (n1_tag + 1)),
    )
    global_k[J0, J0] += local_k[I0, I0]
    global_k[J0, J1] += local_k[I0, I1]

    global_k[J1, J0] += local_k[I1, I0]
    global_k[J1, J1] += local_k[I1, I1]

    return global_k


def add_to_global_vector(
    n0_tag: TagType,
    n1_tag: TagType,
    global_v: Vec,
    local_v: Vec,
) -> Vec:
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
