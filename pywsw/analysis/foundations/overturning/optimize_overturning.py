__all__ = ['optimize']

from dataclasses import dataclass, field
import numpy as np
from scipy.optimize import shgo as scipy_shgo, Bounds, OptimizeResult as ScipyResult
from typing import Sequence

from pywsw.core import set_units
from pywsw.analysis.foundations.overturning import (
    stability,
    bearing
)


@dataclass(kw_only=True)
class OptimizeResult:
    """Result of optimization

    Unit are assumed consistent.

    Attributes
    ----------
    l_toe: float
        Toe length
    l_heel: float
        Heel length
    l_brg: float
        Length of bearing on footing (e.q., stem thickness or pier depth).
    h_ftg: float
        Footing height
    b_ftg: float
        Footing width
    sf: float
        Safety factor against overturning
    q_max: float
        Maximum bearing pressure
    sol
        Raw solution from ``scipy.optimize.shgo``.
    """
    l_toe: float = np.nan
    l_heel: float = np.nan
    l_brg: float = np.nan
    h_ftg: float = np.nan
    b_ftg: float = np.nan
    sf: float = np.nan
    q_max: float = np.nan
    sol: ScipyResult = field(default_factory=ScipyResult, repr=False)

    @property
    def l_ftg(self) -> float:
        """Footing length"""
        return self.l_toe + self.l_heel + self.l_brg

    @property
    def area(self):
        """Footing sectional area"""
        return self.l_ftg*self.h_ftg

    @property
    def volume(self):
        """Footing volume"""
        return self.area*self.b_ftg

    @property
    def valid(self):
        """Is the solution valid?"""
        return hasattr(self.sol, 'success') and self.sol.success


@set_units(ret_units=None,
           arg_units=('ft', 'ft', 'ft', 'ft', 'ft', 'lbf*ft', 'lbf',
                      'lbf/ft^2', None, 'lbf/ft^2', 'lbf/ft^2', 'lbf/ft^3',
                      None, None, None, None))
def optimize(
        l_t: float|Sequence[float],
        l_h: float|Sequence[float],
        h: float|Sequence[float],
        b: float|Sequence[float],
        l_brg: float,
        M_ot: float,
        W: float = 0,
        allow_bearing_pressure: float = 1500.0,
        min_safety_factor: float = 1.5,
        w_t: float = 0.0,
        w_h: float = 0.0,
        gamma_c: float = 150.0,
        force_centered: bool = False,
        max_iterations: int = 3,
        max_samples: int = 100,
        verbose: bool = False,
) -> OptimizeResult:
    """
    Find optimum footing dimensions for given design criteria.

    *Note:* Assumes consistent units. If units other than feet and pounds
    are used, ``allow_bearing_pressure`` and ``gamma_c`` must be provided.

    Minimize footing volume subject to the dimensional bounds, stability
    criteria, and allowable bearing pressure provided.

    Parameters
    ----------
    l_t: float or (float, float)
        Toe length bounds. A provided scalar ``x`` will be interpreted as ``(x, x)``.
    l_h: float or (float, float)
        Heel length bounds. A provided scalar ``x`` will be interpreted as ``(x, x)``.
    h: float or (float, float)
        Footing height bounds. A provided scalar ``x`` will be interpreted as ``(x, x)``.
    b: float or (float, float)
        Footing width bounds. A provided scalar ``x`` will be interpreted as ``(x, x)``.
    l_brg: float
        Length of bearing on footing (e.q., stem thickness or pier depth).
    M_ot: float
        Overturning moment on footing.
    W: float
        Lineal load on footing including stem, pier, etc.
    allow_bearing_pressure: float
        Allowable bearing pressure. Defaults to ``1500.0``.
    min_safety_factor: float
        Minimum allowable safety factor. Defaults to ``1.5``.
    w_t: float
        Overburden pressure on toe. Defaults to ``0.0``.
    w_h: float
        Overburden pressure on heel. Defaults to ``0.0``.
    gamma_c: float
        Concrete unit weight. Defaults to ``150.0``.
    force_centered: bool
        Force the footing to be centered. Defaults to ``False``.
    max_iterations: int
        Maximum solution space sampling iterations. Used by
        ``scipy.optimize.shgo``. Defaults to ``3``.
    max_samples: int
        Maximum solution space samples. Used by
        ``scipy.optimize.shgo``. Defaults to ``100``.
    verbose: bool
        Print the raw solution from ``scipy.optimize.shgo``. Defaults to ``False``.

    Returns
    -------
    result : OptimizeResult
        Result of the optimization. Check ``result.valid`` to verify a valid solution was found.
    """

    # boundary (geometry) constraints
    bounds = _make_bounds(l_t, l_h, h, b)

    # partial design functions
    fkwargs = dict(l_brg=l_brg,
                   M_ot=M_ot,
                   W=W,
                   w_t=w_t,
                   w_h=w_h,
                   gamma_c=gamma_c)

    fS = (lambda X:
          stability(X[0], X[1], h=X[2], b=X[3], **fkwargs) - min_safety_factor)

    fB = (lambda X:
          allow_bearing_pressure - bearing(X[0], X[1], h=X[2], b=X[3], **fkwargs)[0])

    fCtr = lambda X: -(X[0]-X[1])**2

    fObjective = lambda X: (X[0]+X[1]+l_brg)*X[2]*X[3] # Volume

    # nonlinear (stability, bearing) constraints
    if force_centered:
        constraints = ({'type': 'ineq', 'fun': fS},
                       {'type': 'ineq', 'fun': fB},
                       {'type': 'ineq', 'fun': fCtr})
    else:
        constraints = ({'type': 'ineq', 'fun': fS},
                       {'type': 'ineq', 'fun': fB})

    solution = scipy_shgo( # type: ignore
        func=fObjective,
        bounds=bounds,
        constraints=constraints,
        n=max_samples,
        iters=max_iterations,
    )

    if verbose:
        print(f"Solution:\n{solution}\n")

    if solution.success:
        return OptimizeResult(
            l_toe=float(solution.x[0]),
            l_heel=float(solution.x[1]),
            l_brg=l_brg,
            h_ftg=float(solution.x[2]),
            b_ftg=float(solution.x[3]),
            sf=float(fS(solution.x) + min_safety_factor),
            q_max=float(fB(solution.x) + allow_bearing_pressure),
            sol=solution,
        )
    else:
        return OptimizeResult(
            sol=solution,
        )

def _make_bounds(
        l_t: float | Sequence[float],
        l_h: float | Sequence[float],
        h: float | Sequence[float],
        b: float | Sequence[float],
) -> Bounds:
    bmin, bmax = [], []
    for xi in (l_t, l_h, h, b):
        if isinstance(xi, float|int):
            bmin.append(xi)
            bmax.append(xi)
        elif isinstance(xi, Sequence) and len(xi) == 1:
            bmin.append(xi[0])
            bmax.append(xi[0])
        elif isinstance(xi, Sequence) and len(xi) >= 2:
            bmin.append(xi[0])
            bmax.append(xi[1])
        else:
            raise ValueError(f"Unknown bounds type: {type(xi)}: {xi}") # noqa
    return Bounds(lb = bmin, ub = bmax)


if __name__ == '__main__':
    res = optimize(
        l_t = (0.667, 3.0),
        l_h = (0.667, 3.0),
        h = (0.833, 3.0),
        b = 1.0,
        l_brg = 0.667,
        M_ot = 1000,
        W = 0,
        w_t = 125,
        w_h = 500,
        allow_bearing_pressure=1500,
        min_safety_factor=1.5,
        force_centered=False,
        gamma_c = 150.0,
    )
    print(res)
