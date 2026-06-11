__all__ = [
    "stability",
    "bearing",
]

import numpy as np

from pywsw.core import set_units

_1_6 = 1.0/6.0
_1_3 = 1.0/3.0
_1_2 = 1.0/2.0
_2_3 = 2.0/3.0


@set_units(ret_units=None,
           arg_units=('ft', 'ft', 'ft', 'ft', 'ft', 'lbf*ft', 'lbf',
                      'lbf/ft^2', 'lbf/ft^2', 'lbf/ft^3'))
def stability(
    l_t: float,
    l_h: float,
    l_brg: float,
    h: float,
    b: float,
    M_ot: float,
    W: float,
    w_t: float,
    w_h: float,
    gamma_c: float,
) -> float:
    """
    Compute the overturning safety factor for a footing.

    Parameters
    ----------
    l_t: float
        Toe length.
    l_h: float
        Heel length.
    l_brg: float
        Load bearing length.
    h: float
        Footing height.
    b: float
        Footing width.
    M_ot: float
        Overturning moment.
    W: float
        Lineal load applied to footing.
    w_t: float
        Superimposed area load on toe of footing.
    w_h: float
        Superimposed area load on heel of footing.
    gamma_c: float
        Unit weight of concrete.

    Returns
    -------
    float
        Calculated Safety Factor
    """
    l = l_t + l_h + l_brg # total footing length

    # return infinite safety factor if M_ot is nearly zero
    if np.isclose(M_ot, 0.0):
        return np.inf

    M_r = (
        _1_2*b*w_t*l_t**2 +                       # toe surcharge
        W*(l_t + _1_2*l_brg) +                    # load
        _1_2*b*w_h*l_h*(l_t + l_brg + _1_2*l_h) + # heel surcharge
        _1_2*b*gamma_c*h*l**2                     # footing weight
    )

    return M_r/M_ot


@set_units(ret_units=None,
           arg_units=('ft', 'ft', 'ft', 'ft', 'ft', 'lbf*ft', 'lbf',
                      'lbf/ft^2', 'lbf/ft^2', 'lbf/ft^3'))
def bearing(
        l_t: float,
        l_h: float,
        l_brg: float,
        h: float,
        b: float,
        M_ot: float,
        W: float,
        w_t: float,
        w_h: float,
        gamma_c: float,
) -> tuple[float, float]:
    """
    Compute the maximum and minimum bearing pressures.

    *Assumes consistent units.*

    Parameters
    ----------
    l_t: float
        Toe length.
    l_h: float
        Heel length.
    l_brg: float
        Load bearing length.
    h: float
        Footing height.
    b: float
        Footing width.
    M_ot: float
        Overturning moment.
    W: float
        Lineal load applied to footing.
    w_t: float
        Superimposed area load on toe of footing.
    w_h: float
        Superimposed area load on heel of footing.
    gamma_c: float
        Unit weight of concrete.

    Returns
    -------
    float, float
        Maximum and minimum bearing pressure.
    """
    l = l_t + l_h + l_brg
    s = _1_6 * l**2

    # Total Downwards Load
    N = (b*l_t*w_t +    # toe surcharge
         W +            # load
         b*l_h*w_h +    # heel surcharge
         gamma_c*b*l*h) # footing weight

    # Resisting Moment
    M_r = (_1_2*b*w_t*l_t**2 +             # toe surcharge
           W*(l_t + _1_2*l_brg) +          # load
           _1_2*b*w_h*l_h*(l - _1_2*l_h) + # heel surcharge
           _1_2*gamma_c*b*h*l**2)          # footing weight

    x0 = (M_r - M_ot)/N # Distance from toe to reaction.
    ecc = _1_2*l - x0   # Eccentricity from footing centerline.

    if x0 < 0:
        return np.inf, -np.inf

    if np.abs(ecc) > _1_6:
        return _2_3*N/x0, 0

    return N/l + np.abs(M_r - M_ot)/s, N/l - np.abs(M_r - M_ot)/s
