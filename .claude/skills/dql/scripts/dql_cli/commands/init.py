import argparse
import pathlib
import shutil
import time

from .. import client, ontology
from ..credentials import CREDENTIALS_PATH
from ._base import Command


class InitCommand(Command):
    name = "init"
    help = "Refresh the ontology cache and reset the tmp workspace."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--max-age",
            type=int,
            default=0,
            help="Skip the ontology re-download if the local copy is younger than N seconds (default: 0 = always refresh).",
        )
        parser.add_argument(
            "--keep-tmp",
            action="store_true",
            help="Don't clear ~/.diffbot/tmp.",
        )

    def run(self, args: argparse.Namespace) -> int:
        base = pathlib.Path.home() / ".diffbot"
        base.mkdir(exist_ok=True)
        tmp = base / "tmp"
        if not args.keep_tmp:
            if tmp.exists():
                shutil.rmtree(tmp)
            tmp.mkdir()

        ont = ontology.ONTOLOGY_PATH
        fresh = ont.exists() and args.max_age > 0 and (time.time() - ont.stat().st_mtime) < args.max_age
        if fresh:
            print(f"ontology: cached ({int(time.time() - ont.stat().st_mtime)}s old)")
        else:
            client.refresh_ontology(ont)
            print(f"ontology: refreshed -> {ont}")

        if CREDENTIALS_PATH.exists():
            print(f"credentials: present at {CREDENTIALS_PATH}")
        else:
            print(
                f"credentials: MISSING at {CREDENTIALS_PATH}\n"
                "  create with: echo \"token=YOUR_TOKEN\" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials"
            )
            return 2
        return 0


COMMAND = InitCommand()
