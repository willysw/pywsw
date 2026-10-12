import math
from collections.abc import Iterable
from itertools import batched
from typing import Any

from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

from .dowel_types import DowelInfo, DowelMember


def _format_item(obj, tag, fmt, unit) -> tuple[str, str]:
    if obj is None:
        return ("", "")
    elif isinstance(obj, (float, int)):
        if math.isnan(obj) or math.isinf(obj):
            return (f"{tag!s}=", "n/a")
        else:
            return (f"{tag!s}=", f"{obj:{fmt}}{unit}")
    else:
        return (f"{tag!s}:", f"{obj!s}")


def _format_pairs(items: Iterable[tuple[str, str]]) -> list[str]:
    out: list[str] = []
    for i in items:
        out.extend(i)
    return out


def _add_item_rows(
    grid: Table, items: Iterable[tuple[Any, str, str, str]], columns: int = 3
) -> Table:
    for i in range(columns):
        grid.add_column(justify="right")
        grid.add_column(justify="left")
    for i in batched(items, columns):
        grid.add_row(*_format_pairs(tuple(_format_item(*j) for j in i)))
    return grid


def _fastener_panel(info: DowelInfo) -> Panel:
    if info.fastener.type:
        title = (
            f"{info.fastener.size} {info.fastener.subtype} {info.fastener.type}"
            if info.fastener.subtype
            else f"{info.fastener.size} {info.fastener.type}"
        )
    else:
        title = "Fastener"
    if info.dowel.double_shear:
        title = f"{title} (Double Shear)"
    else:
        title = f"{title} (Single Shear)"

    items = (
        (info.fastener.diameter, "D", "0.4f", "in"),
        (info.fastener.root_diameter, "Dr", "0.4f", "in"),
        (info.fastener.fyb, "Fyb", "0.1f", "psi"),
        (info.fastener.length, "L", "0.3f", "in"),
        (info.fastener.thread_length, "Lt", "0.3f", "in"),
    )
    grid = Table.grid(expand=True)
    grid = _add_item_rows(grid, items, 3)
    return Panel(grid, title=title, style="bold")


def _member_panel(info: DowelInfo, which: DowelMember.MemberType) -> Panel:

    member, fe, material = (
        (info.main, info.dowel.Fe_m, info.dowel.type_m)
        if which == DowelMember.MemberType.MAIN
        else (info.side, info.dowel.Fe_s, info.dowel.type_s)
    )

    title = f"{which.name.capitalize()} Member ({material.name.capitalize()})"

    items = (
        (member.thickness, "l", "0.3f", "in"),
        (member.theta, "θ", "0.1f", "deg"),
        (member.specific_gravity, "sg", "0.3f", ""),
        (fe, "Fe", "0.1f", "psi"),
    )
    grid = Table.grid(expand=True)
    grid = _add_item_rows(grid, items, 2)
    return Panel(grid, title=title, style="bold")


def _factor_panel(info: DowelInfo) -> Panel:
    dowel = info.dowel
    items = (
        (dowel.R_e, "Re", "0.4f", ""),
        (dowel.R_t, "Rt", "0.4f", ""),
        (None, "", "", ""),
        (None, "", "", ""),
        (dowel.k[1], "k1", "0.4f", ""),
        (dowel.k[2], "k2", "0.4f", ""),
        (dowel.k[3], "k3", "0.4f", ""),
        (None, "", "", ""),
        (dowel.R_d[1], "Rd1", "0.4f", ""),
        (dowel.R_d[2], "Rd2", "0.4f", ""),
        (dowel.R_d[3], "Rd3", "0.4f", ""),
        (dowel.R_d[4], "Rd4", "0.4f", ""),
    )
    grid = Table.grid(expand=True)
    grid = _add_item_rows(grid, items, 4)
    return Panel(grid, title="Factors", style="bold")


def _capacity_panel(info: DowelInfo) -> Panel:
    cap = info.dowel.Z
    items = (
        (cap.zIm, "zIm", "0.2f", "lb"),
        (cap.zIs, "zIs", "0.2f", "lb"),
        (cap.zII, "zII", "0.2f", "lb"),
        (cap.zIIIm, "zIIIm", "0.2f", "lb"),
        (cap.zIIIs, "zIIIs", "0.2f", "lb"),
        (cap.zIV, "zIV", "0.2f", "lb"),
    )
    grid = Table.grid(expand=True)
    grid = _add_item_rows(grid, items, 3)

    res = Align.center(
        Panel.fit(
            f"Z'={cap.z:0.2f} governed by mode {cap.mode!s}", style="cyan bold"
        )
    )
    return Panel(Group(grid, res), title="Capacity", style="bold")


def print_dowel_output(
    info: DowelInfo,
    console: Console | None = None,
) -> None:
    console = Console() if console is None else console

    console.print(_fastener_panel(info))

    members = Table.grid(expand=True)
    members.add_row(
        _member_panel(info, DowelMember.MemberType.MAIN),
        _member_panel(info, DowelMember.MemberType.SIDE),
    )
    console.print(members)

    console.print(_factor_panel(info))
    console.print(_capacity_panel(info))
