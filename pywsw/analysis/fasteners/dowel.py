from collections.abc import Iterable
from dataclasses import InitVar, dataclass, field
from enum import StrEnum
from math import inf
from typing import NamedTuple, overload

import numpy as np


class FailureModes(NamedTuple):
    zIm: float
    zIs: float
    zII: float
    zIIIm: float
    zIIIs: float
    zIV: float

    @property
    def mode(self) -> str:
        return self._fields[self.index(min(self))]

    @property
    def z(self) -> float:
        return min(self)


@dataclass
class Dowel:
    class MATERIAL_TYPE(StrEnum):
        WOOD = "wood"
        STEEL = "steel"
        CONCRETE = "concrete"

    d: float
    f_yb: float
    l_s: float
    l_m: float
    double_shear: bool = False

    type_s: MATERIAL_TYPE = field(default=MATERIAL_TYPE.WOOD, repr=False)
    sg_s: float = field(default=0.5, repr=False)
    theta_s: float = field(default=90.0, repr=False)
    type_m: MATERIAL_TYPE = field(default=MATERIAL_TYPE.WOOD, repr=False)
    sg_m: float = field(default=0.5, repr=False)
    theta_m: float = field(default=90.0, repr=False)

    use_radians: bool = field(default=False, repr=False, kw_only=True)
    strict: bool = field(default=True, repr=False, kw_only=True)
    theta: InitVar[float | None] = field(init=True, default=None, kw_only=True)
    sg: InitVar[float | None] = field(init=True, default=None, kw_only=True)

    def __post_init__(self, theta: float | None, sg: float | None) -> None:
        if theta is not None:
            self.theta_s = float(theta)
            self.theta_m = float(theta)

        if sg is not None:
            self.sg_s = float(sg)
            self.sg_m = float(sg)

    @property
    def Fe_s(self) -> float:
        match self.type_s:
            case Dowel.MATERIAL_TYPE.STEEL:
                return 87000.0
            case Dowel.MATERIAL_TYPE.CONCRETE:
                return 45000.0
            case _:
                return self.calc_Fe(
                    self.d,
                    self.sg_s,
                    self.theta_s,
                    use_radians=self.use_radians,
                    strict=self.strict,
                )

    @property
    def Fe_m(self) -> float:
        match self.type_s:
            case Dowel.MATERIAL_TYPE.STEEL:
                return 87000.0
            case Dowel.MATERIAL_TYPE.CONCRETE:
                return 45000.0
            case _:
                return self.calc_Fe(
                    self.d,
                    self.sg_m,
                    self.theta_m,
                    use_radians=self.use_radians,
                    strict=self.strict,
                )

    @property
    def R_e(self) -> float:
        return self.Fe_m / self.Fe_s

    @property
    def R_t(self) -> float:
        return self.l_m / self.l_s

    @property
    def k(self) -> np.ndarray:
        return self.calc_k(
            self.R_e, self.R_t, self.d, self.f_yb, self.Fe_m, self.l_s, self.l_m
        )

    @property
    def R_d(self) -> np.ndarray:
        return self.calc_Rd(self.d, strict=self.strict)

    @property
    def Z(self) -> FailureModes:
        return self.calc_Z(
            d=self.d,
            f_yb=self.f_yb,
            l_m=self.l_m,
            l_s=self.l_s,
            theta_m=self.theta_m,
            sg_m=self.sg_m,
            theta_s=self.theta_s,
            sg_s=self.sg_s,
            double_shear=self.double_shear,
            use_radians=self.use_radians,
            strict=self.strict,
        )

    @classmethod
    def calc_Z(
        cls,
        d: float,
        f_yb: float,
        l_m: float,
        l_s: float,
        theta_m: float = 0.0,
        sg_m: float = 0.5,
        theta_s: float = 0.0,
        sg_s: float = 0.5,
        *,
        double_shear: bool = False,
        theta: float | None = None,
        sg: float | None = None,
        use_radians: bool = False,
        strict: bool = True,
    ) -> FailureModes:
        if theta is not None:
            theta_m, theta_s = theta, theta
        if sg is not None:
            sg_m, sg_s = sg, sg

        f_es = cls.calc_Fe(
            d, sg_s, theta_s, use_radians=use_radians, strict=strict
        )
        f_em = cls.calc_Fe(
            d, sg_m, theta_m, use_radians=use_radians, strict=strict
        )
        r_d = cls.calc_Rd(d, strict=strict)
        r_e, r_t = f_em / f_es, l_m / l_s
        k = cls.calc_k(r_e, r_t, d, f_yb, f_em, l_s, l_m)

        if double_shear:
            return FailureModes(
                zIm=float((d * l_m * f_em) / r_d[1]),
                zIs=float(2 * (d * l_s * f_es) / r_d[1]),
                zII=inf,
                zIIIm=inf,
                zIIIs=float(
                    2 * (k[3] * d * l_s * f_es) / ((1 + 2 * r_e) * r_d[3])
                ),
                zIV=float(
                    (2 * d**2 / r_d[4])
                    * np.sqrt((2 / 3) * ((f_em * f_yb) / (1 + r_e)))
                ),
            )
        else:
            return FailureModes(
                zIm=float((d * l_m * f_em) / r_d[1]),
                zIs=float((d * l_s * f_es) / r_d[1]),
                zII=float((k[1] * d * l_s * f_es) / r_d[2]),
                zIIIm=float((k[2] * d * l_m * f_em) / ((1 + 2 * r_e) * r_d[3])),
                zIIIs=float((k[3] * d * l_s * f_es) / ((1 + 2 * r_e) * r_d[3])),
                zIV=float(
                    (d**2 / r_d[4])
                    * np.sqrt((2 / 3) * ((f_em * f_yb) / (1 + r_e)))
                ),
            )

    @staticmethod
    def calc_Fe(
        d: float,
        sg: float,
        theta: float,
        *,
        use_radians: bool = False,
        strict: bool = True,
    ) -> float:
        if not use_radians:
            theta = np.deg2rad(theta)

        fe_small = 16600.0 * sg**1.84
        fe_para = 11200.0 * sg
        fe_perp = 6100 * (sg**1.45) / (d**0.5)
        fe_big = (fe_para * fe_perp) / (
            fe_para * np.sin(theta) ** 2 + fe_perp * np.cos(theta) ** 2
        )
        fe_out = np.where(d < 0.25, fe_small, fe_big)

        return fe_out if (fe_out.size > 1) else fe_out.item()

    @staticmethod
    def calc_k(
        r_e: float,
        r_t: float,
        d: float,
        f_yb: float,
        f_em: float,
        l_s: float,
        l_m: float,
    ) -> np.ndarray:
        k1 = (
            np.sqrt(
                r_e + 2 * (r_e**2) * (1 + r_t + r_t**2) + (r_t**2) * (r_e**3)
            )
            - (r_e * (1 + r_t))
        ) / (1 + r_e)

        c1 = (2 * f_yb * (d**2)) / (3 * f_em)

        if k1.size == 1:
            k1 = np.full_like(c1, k1.item())

        k2 = np.sqrt(2 * (1 + r_e) + c1 * (1 + 2 * r_e) / (l_m**2)) - 1

        k3 = np.sqrt(2 * (1 + r_e) / r_e + c1 * (2 + r_e) / (l_s**2)) - 1

        return np.array((np.zeros_like(k1), k1, k2, k3), dtype=float)

    @staticmethod
    def calc_Rd(d: float, *, strict: bool = True) -> np.ndarray:
        """Compute Rd for the given diameter.

        Arguments
        ---------
        d : float
            Dowel diameter.

        Keyword Arguments
        -----------------
        strict : bool
            If `True`, use the exact equations in the NDS. If `False`, use
            modified equations to correct the discontinuity between 0.25
            and 0.50 inches. Defaults to `True`.
        """
        if strict:
            rd_small = np.interp(
                d, (0.17, 0.25), (2.2, 3.0), left=2.2, right=3.0
            )
            rd1 = np.where(d <= 0.25, rd_small, 4.0)
            rd2 = np.where(d <= 0.25, rd_small, 3.6)
            rd3 = np.where(d <= 0.25, rd_small, 3.2)
            rd4 = np.where(d <= 0.25, rd_small, 3.2)
        else:
            rd1 = np.interp(d, (0.17, 0.35), (2.2, 4.0), left=2.2, right=4.0)
            rd2 = np.interp(d, (0.17, 0.31), (2.2, 3.6), left=2.2, right=3.6)
            rd3 = np.interp(d, (0.17, 0.27), (2.2, 3.2), left=2.2, right=3.2)
            rd4 = np.interp(d, (0.17, 0.27), (2.2, 3.2), left=2.2, right=3.2)
        return np.asarray((np.zeros_like(d), rd1, rd2, rd3, rd4))

    @overload
    @staticmethod
    def fyb_by_diameter(d: float, *, strict: bool = True) -> float: ...
    @overload
    @staticmethod
    def fyb_by_diameter(
        d: Iterable[float], *, strict: bool = True
    ) -> np.ndarray: ...
    @staticmethod
    def fyb_by_diameter(
        d: float | Iterable[float],
        *,
        strict: bool = True,
    ) -> float | np.ndarray:
        """Calculate the default bending yield stress given the fastener diameter.

        Arguments
        ---------
        d : float | Iterable[float]
            Fastener diameter in inches.
        strict : bool, Optional
            If `False`, use linear intrpolation to smooth the curves. Otherwise, use
            stepped data to match the NDS tables. Defaults to `True`.

        Returns
        -------
        float | NDArray[float]
            Bending yield stress in pounds per square inch (psi).
        """
        # NDS T12L(2), T12J(2)
        dia = np.asarray(d)
        DIA = np.array(
            (-np.inf, 0.142, 0.177, 0.236, 0.273, 0.3125, 0.375, np.inf)
        )
        FYB = np.array(
            (
                100000.0,
                100000.0,
                90000.0,
                80000.0,
                70000.0,
                60000.0,
                45000.0,
                45000.0,
            )
        )
        if strict:
            fyb = FYB[np.searchsorted(DIA, dia)]
        else:
            fyb = np.interp(dia, DIA, FYB)

        if fyb.size > 1:
            return fyb
        else:
            return fyb.item()


__all__ = ("Dowel",)
