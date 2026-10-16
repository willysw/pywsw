import math

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pywsw.analysis.fasteners import Dowel
from pywsw.cli.prompt import Confirm, FloatPrompt, Prompt
from pywsw.data import DataLoader

from .dowel_types import DowelFastener, DowelInfo


def load_dowel_list() -> pd.DataFrame:
    return DataLoader.get_csv("dowel_table")


def _ask_type(
    dwl: DowelFastener, df: pd.DataFrame, console: Console
) -> tuple[DowelFastener, pd.DataFrame]:
    type_list: list[str] = sorted(df["Type"].unique()) + ["Generic"]
    type = Prompt.ask(
        "Select fastener type",
        choices=type_list,
        default="Generic",
        case_sensitive=False,
        console=console,
    )
    if type == "Generic":
        return dwl._replace(type=type), df
    else:
        return dwl._replace(type=type), df.loc[df["Type"] == type]


def _ask_generic(dwl: DowelFastener, console: Console) -> DowelFastener:
    d = FloatPrompt.ask("Diameter (in)", console=console)
    d_r = FloatPrompt.ask("Inner diameter (in)", default=d, console=console)
    default_fyb = Dowel.fyb_by_diameter(d)
    fyb = FloatPrompt.ask(
        "Bending yield stress (psi)", default=default_fyb, console=console
    )
    l = FloatPrompt.ask("Length", default=None, console=console)
    l = l if l else math.nan
    l_thread = FloatPrompt.ask(
        "Threaded length", default=None if math.isnan(l) else l, console=console
    )
    l_thread = l_thread if l_thread else math.nan
    return DowelFastener(
        diameter=d,
        root_diameter=d_r,
        fyb=fyb,
        length=l,
        thread_length=l_thread,
    )


def _ask_subtype(
    dwl: DowelFastener, df: pd.DataFrame, console: Console
) -> tuple[DowelFastener, pd.DataFrame]:
    subtype_list: list[str] = sorted(
        k for k in df["Subtype"].unique() if not pd.isna(k)
    )
    if subtype_list:
        subtype = Prompt.ask(
            f"Select {dwl.type} subtype",
            choices=subtype_list,
            case_sensitive=False,
            console=console,
        )
        return dwl._replace(subtype=subtype), df.loc[df["Subtype"] == subtype]
    else:
        return dwl, df


def _print_size_table(
    dwl: DowelFastener, df: pd.DataFrame, console: Console
) -> None:
    fields: dict[str, tuple[str, ...]] = {
        "Size": ("Size", ""),
        "D": ("Outer Diam", "0.4f"),
        "D_r": ("Inner Diam", "0.4f"),
        "L": ("Length", "0.3f"),
        "L_thread": ("Thread Length", "0.3f"),
        "Fyb": ("Fyb", ".1f"),
    }
    for k in [f for f in fields]:
        if all(df[k].isna()) or all(df[k] == ""):
            del fields[k]

    title_text = (
        f"{dwl.type!s}, {dwl.subtype!s}" if dwl.subtype else f"{dwl.type!s}"
    )
    tab_out = Table(
        expand=True,
        row_styles=("dim", ""),
    )

    for v, _ in fields.values():
        tab_out.add_column(v, justify="center")
    tab_out.columns[0].style = "bold green"

    for _, row_i in df.iterrows():
        row_args = [
            (f"{row_i[k]:{fmt}}" if fmt else f"{row_i[k]!s}")
            for k, (_, fmt) in fields.items()
        ]
        tab_out.add_row(*row_args)

    console.print(Panel(tab_out, title=title_text, style="bold"))


def _ask_size(
    dwl: DowelFastener, df: pd.DataFrame, console: Console
) -> tuple[DowelFastener, pd.DataFrame]:
    size_list: list[str] = sorted(df["Size"].unique())
    query = (
        f"Select {dwl.type}, {dwl.subtype} size"
        if dwl.subtype
        else f"Select {dwl.type} size"
    )
    size = Prompt.ask(
        query,
        choices=size_list,
        show_choices=False,
        case_sensitive=False,
        console=console,
    )
    return dwl._replace(size=size), df.loc[df["Size"] == size]


def _ask_if_empty_fyb(dowel: DowelFastener, console: Console) -> DowelFastener:
    if math.isnan(dowel.fyb):
        return dowel._replace(
            fyb=FloatPrompt.ask(
                "Specify bending yield stress Fyb (psi)",
                default=Dowel.fyb_by_diameter(dowel.diameter),
                console=console,
            )
        )
    return dowel


def _get_data(dwl: DowelFastener, df: pd.DataFrame) -> DowelFastener:
    dowel = df[df["Size"] == dwl.size].iloc[0]
    return dwl._replace(
        diameter=dowel["D"].item() if pd.notna(dowel["D"]) else math.nan,
        root_diameter=dowel["D_r"].item()
        if pd.notna(dowel["D_r"])
        else math.nan,
        length=dowel["L"].item() if pd.notna(dowel["L"]) else math.nan,
        thread_length=(
            dowel["L_thread"].item()
            if pd.notna(dowel["L_thread"])
            else math.nan
        ),
        fyb=dowel["Fyb"].item() if pd.notna(dowel["Fyb"]) else math.nan,
    )


def _ask_which_diameter(
    dowel: DowelFastener, console: Console
) -> DowelFastener:
    if (
        not math.isnan(dowel.diameter)
        and not math.isnan(dowel.root_diameter)
        and not math.isclose(
            dowel.diameter, dowel.root_diameter, abs_tol=0.0001
        )
    ):
        use_root_diameter = Confirm.ask(
            "Use root diameter?", default=True, console=console
        )
        return dowel._replace(use_root_diameter=use_root_diameter)
    else:
        return dowel._replace(use_root_diameter=False)


def ask_load_dowel(console: Console | None = None) -> DowelInfo:
    console = Console() if console is None else console

    console.rule(title="Fastener", style="bold")

    dwl = DowelFastener()
    df = load_dowel_list()

    dwl, df = _ask_type(dwl, df, console)
    if dwl.type == "Generic":
        return _ask_generic(dwl, console)

    dwl, df = _ask_subtype(dwl, df, console)
    _print_size_table(dwl, df, console)
    dwl, df = _ask_size(dwl, df, console)

    # Fill out parameters from the database
    dwl = _get_data(dwl, df)

    # Ask which diameter to use
    dwl = _ask_which_diameter(dwl, console)

    # Ask for fyb if fyb is NAN
    dwl = _ask_if_empty_fyb(dwl, console)

    double_shear = Confirm.ask("Double shear?", default=False, console=console)

    return DowelInfo(fastener=dwl._replace(double_shear=double_shear))
