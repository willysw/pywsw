from collections.abc import Iterable

import numpy as np
from numpy import linalg
from numpy.typing import ArrayLike

from .beam_error import BadConditioning, BadDimensionality, BadSolution
from .types import Arr, IDs, Mat, Vec

IDParts = type[dict[str, IDs]]
MatParts = type[dict[str, Mat]]
VecParts = type[dict[str, Vec]]


def verify_dimensionality(K: Arr, z: Arr, f: Arr, r: Arr) -> bool:
    """Verify the dimensionalities of the input arrays.

    Parameters
    ----------
    K : Array2D
        Stiffness matrix.
    z : Array1D
        Displacement vector.
    f : Array1D
        Node load vector.
    r : Array1D
        Reaction vector.

    Returns
    -------
    bool
        True if all checks passed.

    Raises
    ------
    BadDimensionality
        Raised if any dimensionality is inconsistent with the problem structure.
    """
    # Check K matrix
    if (K.ndim != 2) or (K.shape[0] != K.shape[1]):
        raise BadDimensionality(
            f"(N,N) matrix expected for K, shape {K.shape} passed."
        )
    n: int = K.shape[0]

    # Check vectors
    for v, vname in zip((z, f, r), "zfr"):
        if v.shape != (n,):
            raise BadDimensionality(
                f"({n:d},) vector expected for {vname!s}, shape {v.shape} passed."
            )

    return True


def verify_conditioning(K: Mat, z: Vec, f: Vec, r: Vec) -> bool:
    """Verify conditioning of arrays.

    Parameters
    ----------
    K : Array2D[float]
        Stiffness matrix, must be square n x n.
    z : Array1D[float]
        Displacement vector with unknowns marked as NaN.
    f : Array1D[float]
        Node load vector (internal (fixed end) + superimposed forces)
    r : Array1D[float]
        Reaction vector with unknowns marked as NaN.

    Returns
    -------
    bool
        True if all checks passed.

    Raises
    ------
    BadConditioning
        Raised if problem is poorly conditioned.
    """
    # 1. Check minimum supports.
    support_count = sum(np.isnan(r))
    if support_count < 2:
        raise BadConditioning(
            f"Insufficient number of supports: {support_count:d} < 2."
        )

    # 2. Check z and r have consistent unknowns.
    free_count = sum(np.isnan(z))
    if (support_count + free_count) != K.shape[0]:
        raise BadConditioning(
            f"Supported nodes ({support_count:d}) + "
            f"free displacements ({free_count:d}) != "
            f"{K.shape[0]:d}"
        )

    # 3. Check that f has no NaNs.
    if any(np.isnan(f)):
        raise BadConditioning("NaNs are not allowed in the f vector.")

    return True


def get_partitions(
    K: Mat, z: Vec, f: Vec, r: Vec
) -> tuple[
    MatParts,
    VecParts,
    VecParts,
    VecParts,
    IDParts,
]:
    """Make partitioned arrays and vectors.

    Parameters
    ----------
    K : Array2D[float]
        Stiffness matrix
    z : Array1D[float]
        Displacements vector with unknown entries as NaN.
    f : Array1D[float]
        Fixed applied force vector.
    r : Array1D[float]
        Reactions vector with unknown entries as NaN and knowns as 0.0.

    Returns
    -------
    tuple[Kparts, zparts, fparts, rparts, idparts]

    Kparts:
        Dictionary of submatrices keyed by "known,unknown", "known,known",
        "unknown,unknown", "unknown,known".

    zparts, fparts, rparts:
        Dictionary of subvectors keyed by "known", "unknown".

    idparts:
        Dictionary of index arrays keyed by "known_r", "unknown_r",
        "known_z", "unknown_z".
    """

    # Find indices of known and unknown r:
    i_known_r: IDs = np.flatnonzero(np.logical_not(np.isnan(r)))
    i_unknown_r: IDs = np.flatnonzero(np.isnan(r))

    # Find indices of known and unknonw z:
    i_known_z: IDs = np.flatnonzero(np.logical_not(np.isnan(z)))
    i_unknown_z: IDs = np.flatnonzero(np.isnan(z))

    # Verify that i_known_r == i_unknown_z
    assert not (set(i_known_r) is set(i_unknown_z))  # TODO: Make exception

    Kparts: MatParts = {
        "known,unknown": K[i_known_r][:, i_unknown_z],
        "known,known": K[i_known_r][:, i_known_z],
        "unknown,unknown": K[i_unknown_r][:, i_unknown_z],
        "unknown,known": K[i_unknown_r][:, i_known_z],
    }
    zparts: VecParts = {
        "known": z[i_known_z],
        "unknown": z[i_unknown_z],
    }
    fparts: VecParts = {
        "known": f[i_known_r],
        "unknown": f[i_unknown_r],
    }
    rparts: VecParts = {
        "known": r[i_known_r],
        "unknown": r[i_unknown_r],
    }
    ids: IDParts = {
        "known_r": i_known_r,
        "unknown_r": i_unknown_r,
        "known_z": i_known_z,
        "unknown_z": i_unknown_z,
    }
    return Kparts, zparts, fparts, rparts, ids


def compute_unknown_z(
    K_ku: Mat, K_kk: Mat, z_k: Vec, f_k: Vec, r_k: Vec
) -> Vec:
    try:
        return -linalg.matmul(
            linalg.inv(K_ku), linalg.matmul(K_kk, z_k) + f_k + r_k
        )
    except linalg.LinAlgError as err:
        raise BadConditioning(err)


def compute_unknown_r(
    K_uk: Mat, z_k: Vec, K_uu: Mat, z_u: Vec, f_k: Vec
) -> Vec:
    return -(linalg.matmul(K_uk, z_k) + linalg.matmul(K_uu, z_u) + f_k)


def verify_solution(
    K: Mat, z: Vec, f: Vec, r: Vec, *, atol: float = 1.0e-10
) -> bool:
    """Check the solution vectors to ensure the equation `K.z + f + r == 0`.

    Parameters
    ----------
    K : Array2D[float]
        Stiffness matrix.
    z : Array1D[float]
        Displacement vector.
    f : Array1D[float]
        Node load vector (internal (fixed end) + superimposed forces)
    r : Array1D[float]
        Reaction vector.
    atol : float, optional
        Absolute tolerance, by default 1.0e-10

    Returns
    -------
    bool
        `True` if solution is ok.

    Raises
    ------
    BadSolution
        Raised if the error exceeds atol.
    """
    r_error = linalg.matmul(K, z) + f + r
    if all(np.isclose(r_error, 0.0, atol=atol)):
        return True
    else:
        raise BadSolution


def trim_to_tolerance(arrs: Iterable[Arr], atol: float) -> tuple[Arr, ...]:
    return tuple(np.where(np.isclose(a, 0.0, atol=atol), 0.0, a) for a in arrs)


def solve_system(
    K: ArrayLike,
    z: ArrayLike,
    f: ArrayLike,
    r: ArrayLike,
    *,
    atol: float = 1e-12,
) -> tuple[Vec, Vec]:
    """Solve the system `K.z + f + r == 0`.

    Parameters
    ----------
    K : Array2D
        Stiffness matrix, must be square n x n.
    z : Array1D
        Displacement vector with unknowns marked as NaN.
    f : Array1D
        Node load vector (internal (fixed end) + superimposed forces)
    r : Array1D
        Reaction vector with unknowns marked as NaN.

    Returns
    -------
    r, z : tuple[Array1D, Array1D]
        Result vectors.

    Other Parameters
    ----------------
    atol : float
        Values under this tolerance will be truncated to 0.0. Default = 1.0e-12.

    Raises
    ------
    BadDimensionality :
        Raised if array dimensions are incorrect or inconsistent.
    BadConditioning :
        Raised if the matrices or vectors all ill-conditioned.
    BadSolution :
        Raised if the equation `K.z + f + r == 0` is not satified
        when using the solution vectors.
    """
    # 1. Verify inputs
    K, z, f, r = (np.asarray(v, dtype=float) for v in (K, z, f, r))
    verify_dimensionality(K, z, f, r)
    verify_conditioning(K, z, f, r)

    # 1. Get partitions:
    Kp, zp, fp, rp, ip = get_partitions(K, z, f, r)

    # 2. Find unknown z:
    zp["unknown"] = compute_unknown_z(
        Kp["known,unknown"],
        Kp["known,known"],
        zp["known"],
        fp["known"],
        rp["known"],
    )

    # 3. Find unknown r:
    rp["unknown"] = compute_unknown_r(
        Kp["unknown,known"],
        zp["known"],
        Kp["unknown,unknown"],
        zp["unknown"],
        fp["unknown"],
    )

    # 4. Compile result vectors:
    r[ip["unknown_r"]] = rp["unknown"]
    z[ip["unknown_z"]] = zp["unknown"]

    # 5. Check solution
    verify_solution(K, z, f, r)

    return trim_to_tolerance((r, z), atol)


__all__ = ("solve_system",)
