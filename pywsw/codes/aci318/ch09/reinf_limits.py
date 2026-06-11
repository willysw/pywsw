__all__ = ['A_s_max_9_3_3_1', 'A_s_min_9_6_1_2']

from math import sqrt

from pywsw.core import set_units
from pywsw.materials.concrete.reinforcing.ratio import (
    rho_tension_controlled
)


@set_units(ret_units='in^2',
           arg_units=('in', 'in', 'lbf/in^2', 'lbf/in^2',
                      'lbf/in**2', None, None))
def A_s_max_9_3_3_1(
        b_w: float,
        d: float,
        f_c: float,
        f_y: float,
        E_s: float = 30.0e6,  # noqa
        e_c: float = -0.003,
        beta_1: float = 0.85,
) -> float:
    """
    Calculates the maximum area of beam longitudinal reinforcement.

    ACI 318-22 Section 9.3.3.1.

    *Note:* Units assumed as noted below.

    Parameters
    ----------
    b_w: float
        Beam width, inches.
    d: float
        Effective beam depth, inches.
    f_c: float
        Concrete f'c, pounds per square inch.
    f_y: float
        Steel fy, pounds per square inch.
    E_s: float, optional
        Steel elastic modulus, pounds per square inch. Defaults to 30.0e6 psi.
    e_c: float, optional
        Concrete strain limit. Defaults to -0.003.
    beta_1: float, optional
        Concrete stress block factor. Defaults to 0.85.

    Returns
    -------
    float
        Maximum reinforcment area A_s_max, square inches.
    """
    return rho_tension_controlled(f_c, f_y, E_s, e_c, beta_1) * b_w * d


@set_units(ret_units='in^2',
           arg_units=('in', 'in', 'lbf/in^2', 'lbf/in^2'))
def A_s_min_9_6_1_2(
        b_w: float,
        d: float,
        f_c: float,
        f_y: float,
) -> float:
    """
    Calculates the minimum area of reinforcement reinforced beams.

    ACI 318-22 Section 9.6.1.2 Equations (a) and (b).

    *Note:* Units assumed as noted below.

    Parameters
    ----------
    b_w: float
        Beam width, inches.
    d: float
        Effective beam depth, inches.
    f_c: float
        Concrete f'c, pounds per square inch.
    f_y: float
        Steel fy, pounds per square inch.

    Returns
    -------
    float
        Minimum reinforcement area A_s_min, square inches.
    """
    f_cr = min(3 * sqrt(f_c), 200.0)
    return f_cr / f_y * b_w * d
