import math
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from typing import Any

from rich.console import Console
from rich.prompt import Confirm, FloatPrompt

from pywsw.analysis.fasteners import Dowel
from .dowel_list import ask_load_dowel
from .dowel_output import print_dowel_output
from .dowel_types import DowelInfo, DowelMember


def _dowel_cli_args(args: Sequence[str]) -> Namespace:
    parser = ArgumentParser()
    return parser.parse_args(args)


def _ask_members(console: Console) -> tuple[DowelMember, DowelMember]:
    console.print("\n")
    console.rule(title="Main and Side Members", style="bold")

    keep_simple = Confirm.ask(
        "Use simplified theta and specific gravity?", default=True, console=console
    )
    queries = dict[str, tuple[str, dict[str, Any]]]()
    answers = dict[str, float]()
    if keep_simple:
        queries.update(
            {
                "lm": ("Main member thickness (in)", {"default": 1.5}),
                "ls": ("Side member thickness (in)", {"default": 1.5}),
                "theta": ("Load direction (deg)", {"default": 90.0}),
                "sg": ("Specific gravity", {"default": 0.5}),
            }
        )
    else:
        queries.update(
            {
                "lm": ("Main member thickness (in)", {"default": 1.5}),
                "theta_m": ("Main member: load direction (deg)", {"default": 90.0}),
                "sg_m": ("Main member: specific gravity", {"default": 0.5}),
                "ls": ("Side member thickness (in)", {"default": 1.5}),
                "theta_s": ("Side member: load direction (deg)", {"default": 90.0}),
                "sg_s": ("Side member: specific gravity", {"default": 0.5}),
            }
        )

    for ni, (queryi, kwargsi) in queries.items():
        answers[ni] = FloatPrompt.ask(prompt=queryi, console=console, **kwargsi)

    main_member = DowelMember(thickness=answers["lm"])
    side_member = DowelMember(thickness=answers["ls"])
    if keep_simple:
        return (
            main_member._replace(
                theta=answers["theta"], specific_gravity=answers["sg"]
            ),
            side_member._replace(
                theta=answers["theta"], specific_gravity=answers["sg"]
            ),
        )
    else:
        return (
            main_member._replace(
                theta=answers["theta_m"], specific_gravity=answers["sg_m"]
            ),
            side_member._replace(
                theta=answers["theta_s"], specific_gravity=answers["sg_s"]
            ),
        )


def _get_dowel_input(console: Console) -> DowelInfo:
    console.rule(characters=" ")

    fastener = ask_load_dowel(console=console)

    main_member, side_member = _ask_members(console)

    console.rule(characters=" ")
    console.rule(title="Other Criteria", style="bold")
    double_shear = Confirm.ask("Double shear?", default=False, console=console)

    # Adjust fastener lengths
    if math.isnan(fastener.length):
        fastener = fastener._replace(
            length=main_member.thickness + side_member.thickness
        )
    else:
        if fastener.length < main_member.thickness + side_member.thickness:
            main_member = main_member._replace(
                thickness=fastener.length - side_member.thickness
            )

    dowel = Dowel(
        d=fastener.diameter,
        f_yb=fastener.fyb,
        l_s=side_member.thickness,
        l_m=main_member.thickness,
        theta_m=main_member.theta,
        sg_m=main_member.specific_gravity,
        theta_s=side_member.theta,
        sg_s=side_member.specific_gravity,
        double_shear=double_shear,
        use_radians=False,
    )
    return DowelInfo(fastener=fastener, main=main_member, side=side_member, dowel=dowel)


def dowel_cli(args_in: Sequence[str], *, console: Console | None = None) -> None:
    C = Console() if console is None else console

    # Get argument parser
    _ = _dowel_cli_args(args_in)

    # Get user input
    info = _get_dowel_input(console=C)
    C.print("\n")
    print_dowel_output(info, C)
