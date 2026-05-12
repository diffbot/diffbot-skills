import argparse
import importlib
import pkgutil
import sys
from typing import Dict

from .commands._base import Command


def discover_commands() -> Dict[str, Command]:
    from . import commands

    found: Dict[str, Command] = {}
    for mod_info in pkgutil.iter_modules(commands.__path__):
        if mod_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{commands.__name__}.{mod_info.name}")
        cmd = getattr(module, "COMMAND", None)
        if cmd is None:
            continue
        if cmd.name in found:
            raise RuntimeError(f"Duplicate command name: {cmd.name}")
        found[cmd.name] = cmd
    return found


def build_parser(commands: Dict[str, Command]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dql", description="Diffbot DQL CLI")
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    for name in sorted(commands):
        cmd = commands[name]
        cp = sub.add_parser(name, help=cmd.help, description=cmd.help)
        cmd.add_arguments(cp)
        cp.set_defaults(_run=cmd.run)
    return parser


def main(argv=None) -> int:
    commands = discover_commands()
    parser = build_parser(commands)
    args = parser.parse_args(argv)
    try:
        return int(args._run(args) or 0)
    except KeyboardInterrupt:
        return 130
    except SystemExit:
        raise
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
