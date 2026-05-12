import argparse
import pathlib

from .. import client
from ._base import Command


class ExportCommand(Command):
    name = "export"
    help = "Run a DQL query and save the response (CSV/XLS/XLSX/JSON) to a file."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("query", help="DQL query string")
        parser.add_argument("out", help="Destination file path")
        parser.add_argument(
            "--format",
            choices=["csv", "xls", "xlsx", "json"],
            default="csv",
            help="Response format (default csv)",
        )
        parser.add_argument(
            "--spec",
            dest="exportspec",
            default=None,
            help="exportspec, e.g. 'name,Name;nbEmployees,Employees;location.city.name,City'",
        )
        parser.add_argument("--size", type=int, default=25, help="Page size (default 25)")
        parser.add_argument("--from", dest="from_", type=int, default=0, help="Pagination offset")
        parser.add_argument("--filter", default=None, help="Response field filter")

    def run(self, args: argparse.Namespace) -> int:
        req = client.DQLRequest(
            query=args.query,
            size=args.size,
            from_=args.from_,
            format=args.format,
            exportspec=args.exportspec,
            filter=args.filter,
        )
        body = client.execute_raw(req)
        out = pathlib.Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
        print(f"saved: {out} ({len(body)} bytes)")
        return 0


COMMAND = ExportCommand()
