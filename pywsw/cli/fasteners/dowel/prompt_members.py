from rich.console import Console
from rich.prompt import FloatPrompt, Prompt

from pywsw.analysis.fasteners import Dowel

from .dowel_types import DowelFastener, DowelInfo, DowelMember


def _ask_member(
    dowel: DowelFastener,
    which: DowelMember.MemberType,
    console: Console,
    strict: bool = False,
):
    # MATERIAL
    material = Dowel.MATERIAL_TYPE(
        str(
            Prompt.ask(
                f"{which.name.capitalize()} member material",
                case_sensitive=False,
                choices=("Wood", "Steel", "Concrete"),
                default="Wood",
                console=console,
            )
        ).lower()
    )
    match material:
        case Dowel.MATERIAL_TYPE.STEEL:
            sg = 490 / 62.4
            theta = 0.0
        case Dowel.MATERIAL_TYPE.CONCRETE:
            sg = 150 / 62.4
            theta = 0.0
        case Dowel.MATERIAL_TYPE.WOOD:
            sg = FloatPrompt.ask(
                "Specific gravity", default=0.5, console=console
            )
            theta = FloatPrompt.ask(
                "Load direction theta (deg)", default=90.0, console=console
            )

    # THICKNESS
    thickness = FloatPrompt.ask(
        f"{str(which).capitalize()} member thickness (in)",
        default=1.5,
        console=console,
    )

    return DowelMember(
        thickness=thickness,
        theta=theta,
        specific_gravity=sg,
        material=material,
        member=which,
    )


def ask_members(
    info: DowelInfo, *, console: Console, strict: bool = True
) -> DowelInfo:
    console.print("\n")
    console.rule(title="Main Member", style="bold")
    main_member = _ask_member(
        info.fastener,
        DowelMember.MemberType.MAIN,
        console=console,
        strict=strict,
    )

    title = "Side Members" if info.fastener.double_shear else "Side Member"
    console.print("\n")
    console.rule(title=title, style="bold")
    side_member = _ask_member(
        info.fastener,
        DowelMember.MemberType.SIDE,
        console=console,
        strict=strict,
    )
    return info._replace(main=main_member, side=side_member)
