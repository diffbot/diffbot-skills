import argparse
from abc import ABC, abstractmethod


class Command(ABC):
    name: str = ""
    help: str = ""

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None: ...

    @abstractmethod
    def run(self, args: argparse.Namespace) -> int: ...
