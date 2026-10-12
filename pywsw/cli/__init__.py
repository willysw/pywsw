import sys
from argparse import ArgumentParser

from rich.console import Console

from .cli_app_base import CliApp
from .fasteners.dowel import DowelCliApp

CLI_APPS: dict[str, CliApp] = {"dowel": DowelCliApp}


def cli_app() -> None:
    console = Console()

    parser = ArgumentParser(prog="pywsw")
    subparsers = parser.add_subparsers(dest="subcmd")
    for app, app_class in CLI_APPS.items():
        subparsers.add_parser(
            app, parents=(app_class().parser,), conflict_handler="resolve"
        )
    args, subcmdargs = parser.parse_known_args(sys.argv[1:])

    if args.subcmd:
        try:
            CLI_APPS[args.subcmd]().run_app(subcmdargs, console=console)
        except KeyError:
            console.print(f"Unknown subcommand {args.subcmd}.")
            sys.exit(1)
        except KeyboardInterrupt:
            console.print(f"\n{args.subcmd.capitalize()} exited by user.")
            sys.exit(1)

    sys.exit(0)


__all__ = ("cli_app",)
