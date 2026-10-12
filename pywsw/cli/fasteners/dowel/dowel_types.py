import math
from enum import StrEnum
from typing import NamedTuple

from pywsw.analysis.fasteners import Dowel


class DowelFastener(NamedTuple):
    diameter: float = math.nan
    root_diameter: float = math.nan
    length: float = math.nan
    thread_length: float = math.nan
    fyb: float = math.nan
    type: str = ""
    subtype: str = ""
    size: str = ""
    use_root_diameter: bool = False
    double_shear: bool = False

    @property
    def design_diameter(self) -> float:
        if not math.isnan(self.root_diameter) and self.use_root_diameter:
            return self.root_diameter
        else:
            return self.diameter


class DowelMember(NamedTuple):
    thickness: float = math.nan
    theta: float = math.nan
    specific_gravity: float = math.nan
    material: Dowel.MATERIAL_TYPE = Dowel.MATERIAL_TYPE.WOOD

    class MemberType(StrEnum):
        MAIN = "main"
        SIDE = "side"

    member: MemberType = MemberType.MAIN


class DowelInfo(NamedTuple):
    fastener: DowelFastener | None = None
    main: DowelMember | None = None
    side: DowelMember | None = None
    dowel: Dowel | None = None


class DowelInputError(Exception): ...


__all__ = ("DowelFastener", "DowelInfo", "DowelMember")
