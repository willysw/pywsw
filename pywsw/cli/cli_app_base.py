from abc import ABC, abstractmethod
from argparse import ArgumentParser
from functools import cached_property

from rich.console import Console


class CliApp(ABC):
    console: Console

    @abstractmethod
    def run_app(
        self, args: list[str], *, console: Console | None = None
    ) -> None: ...

    @abstractmethod
    @cached_property
    def parser(self) -> ArgumentParser: ...
