import sys
from argparse import ArgumentParser

from . import fasteners


def cli_app() -> None:
    try:
        parser = ArgumentParser(prog="pywsw")
        subparsers = parser.add_subparsers(dest="subcmd")
        subparsers.add_parser("dowel")

        args, subcmdargs = parser.parse_known_args(sys.argv[1:])

        match args.subcmd.lower():
            case "dowel":
                fasteners.dowel.dowel_cli(subcmdargs)
            case str(s):
                print(f"Unknown subcommand {s}.")
                sys.exit(1)
            case _:
                ...

    except KeyboardInterrupt:
        sys.exit(1)

    sys.exit(0)


__all__ = ("cli_app", "fasteners")
