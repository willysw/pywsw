__all__ = ['fK_a', 'fK_p']

from math import cos, sqrt

from pywsw.core import set_units


@set_units(ret_units=None, arg_units=('radians', 'radians'))
def fK_a(
    phi: float,
    beta: float = 0.0
) -> float:
    """
    Calculate Rankine active pressure coefficient Ka.

    *Note:* Units assumed as noted below.

    Parameters
    ----------
    phi: float
        Soil friction angle in radians.
    beta: float, optional
        Slope angle from horizontal in radians. Defaults to 0.

    Returns
    -------
    float:
        Active pressure coefficient Ka
    """
    cb = cos(beta)
    x = sqrt(cb**2 - cos(phi)**2)
    return cb*(cb-x)/(cb+x)


@set_units(ret_units=None, arg_units=('radians', 'radians'))
def fK_p(
    phi: float,
    beta: float = 0.0
) -> float:
    """
    Calculate Rankine passive pressure coefficient Ka.

    *Note:* Units assumed as noted below.

    Parameters
    ----------
    phi: float
        Soil friction angle in radians.
    beta: float
        Slope angle from horizontal in radians. Defaults to 0.

    Returns
    -------
    float
        Passive pressure coefficient Ka
    """
    cb = cos(beta)
    x = sqrt(cb**2 - cos(phi)**2)
    return cb*(cb+x)/(cb-x)
