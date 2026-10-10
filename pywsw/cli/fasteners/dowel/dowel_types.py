from math import nan as NAN
from typing import NamedTuple

from pywsw.analysis.fasteners import Dowel


class DowelFastener(NamedTuple):
    diameter: float = NAN
    inner_diameter: float = NAN
    length: float = NAN
    thread_length: float = NAN
    fyb: float = NAN
    type: str = ""
    subtype: str = ""
    size: str = ""


class DowelMember(NamedTuple):
    thickness: float = NAN
    theta: float = NAN
    specific_gravity: float = NAN


class DowelInfo(NamedTuple):
    fastener: DowelFastener
    main: DowelMember
    side: DowelMember
    dowel: Dowel


__all__ = ("DowelFastener", "DowelInfo", "DowelMember")
