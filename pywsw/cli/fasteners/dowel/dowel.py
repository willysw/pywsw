from argparse import ArgumentParser, Namespace
from functools import cached_property

from rich.console import Console

from pywsw.analysis.fasteners import Dowel
from pywsw.cli import CliApp

from .dowel_output import print_dowel_output
from .dowel_types import DowelInfo, DowelInputError
from .prompt_dowel import ask_load_dowel
from .prompt_members import ask_members
from .validate_geometry import validate_geometry


class DowelCliApp(CliApp):
    console: Console
    strict: bool = False

    def run_app(
        self, args: list[str], *, console: Console | None = None
    ) -> None:
        try:
            self.console = Console() if console is None else console
            self.console.width = min(self.console.width, 80)

            app_args: Namespace = self.parser.parse_args(args)
            self.strict = app_args.strict

            # Get user input
            info = self.get_dowel_input()
            self.console.rule(characters=" ")
            print_dowel_output(info, self.console)
        except DowelInputError as err:
            console.print(str(err))

    @cached_property
    def parser(self) -> ArgumentParser:
        parser = ArgumentParser()
        parser.add_argument(
            "-s",
            "--strict",
            action="store_true",
            help="Attempt to strictly match the values in the NDS tables.",
        )
        return parser

    def get_dowel_input(self) -> DowelInfo:
        self.console.rule(characters=" ")

        info = ask_load_dowel(console=self.console)

        info = ask_members(info, console=self.console, strict=self.strict)

        info = validate_geometry(info)

        info = info._replace(
            dowel=Dowel(
                d=info.fastener.design_diameter,
                f_yb=info.fastener.fyb,
                l_s=info.side.thickness,
                l_m=info.main.thickness,
                type_m=info.main.material,
                theta_m=info.main.theta,
                sg_m=info.main.specific_gravity,
                type_s=info.side.material,
                theta_s=info.side.theta,
                sg_s=info.side.specific_gravity,
                double_shear=info.fastener.double_shear,
                use_radians=False,
            )
        )

        return info
