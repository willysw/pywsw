__all__ = ['rho_by_strain', 'rho_tension_controlled']


def rho_by_strain(
        f_c: float,
        f_y: float,
        e_c: float = -0.003,
        e_s: float = 0.005,
        beta_1: float = 0.85,
) -> float:
    """
    Calculate the reinforcement ratio based on strain conditions.

    Consistent units assumed.

    Parameters
    ----------
    f_c : float
        Compressive strength of concrete.
    f_y : float
        Yield strength of reinforcing steel.
    e_c : float, optional
        Strain in the concrete at the extreme compression fiber, by default -0.003.
    e_s : float, optional
        Tensile strain in the reinforcement, by default 0.005.
    beta_1 : float, optional
        Factor accounting for the shape of the concrete stress block, by default
        0.85.

    Returns
    -------
    float
        Calculated reinforcement ratio.

    Examples
    --------
    >>>rho_by_strain(3000, 60000)

    0.01594
    """
    return -beta_1 * (f_c / f_y) * (e_c / (e_s - e_c))


def rho_tension_controlled(
        f_c: float,
        f_y: float,
        E_s: float, # noqa
        e_c: float = -0.003,
        beta_1: float = 0.85,
) -> float:
    """
    Calculates the tensile-controlled reinforcement ratio for a rectangular cross-section.

    Consistent units assumed.

    Parameters
    ----------
    f_c : float
        Compressive strength of concrete.
    f_y : float
        Yield strength of reinforcing steel.
    E_s : float
        Elastic modulus of reinforcing steel.
    e_c : float, optional
        Strain in the concrete at the extreme compression fiber, by default -0.003.
    beta_1 : float, optional
        Factor accounting for the shape of the concrete stress block, by default
        0.85.

    Returns
    -------
    ArrayLike[float]
        Calculated reinforcement ratio.
    """
    e_s = f_y/E_s + 0.003
    return rho_by_strain(f_c, f_y, e_c, e_s, beta_1)

