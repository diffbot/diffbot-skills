import argparse
import json
import sys

from .. import client
from ._base import Command


class ProbeCommand(Command):
    name = "probe"
    help = "Run multiple DQL queries in parallel and print hit counts (size=0) for each."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("queries", nargs="+", help="One or more DQL query strings")
        parser.add_argument(
            "--workers",
            type=int,
            default=8,
            help="Maximum concurrent requests (default 8)",
        )
        parser.add_argument(
            "--json",
            dest="as_json",
            action="store_true",
            help="Emit results as a JSON array instead of a text table.",
        )

    def run(self, args: argparse.Namespace) -> int:
        reqs = [client.DQLRequest(query=q, size=0) for q in args.queries]
        results = client.execute_parallel(reqs, workers=args.workers)
        rows = [
            {"query": q, "hits": r.get("hits"), "results": r.get("results")}
            for q, r in zip(args.queries, results)
        ]
        if args.as_json:
            sys.stdout.write(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
            return 0
        width = max(len(str(row["hits"])) for row in rows)
        for row in rows:
            sys.stdout.write(f"{str(row['hits']).rjust(width)}  {row['query']}\n")
        return 0


COMMAND = ProbeCommand()
