#!/usr/bin/env python3
"""
Portable launcher for the vendored Diffbot `db` CLI.

Source of truth for vendor/bin/db — scripts/vendor-db.sh copies this file into
the bundle. It adds the vendored dependency tree (vendor/) to sys.path and
dispatches to diffbot.cli:main, so the CLI runs straight from the package with
no virtualenv and no pip install.

The vendored bundle is pinned to a Python 3.9-compatible dependency set (3.9 is
the macOS system interpreter). diffbot-python's own metadata says >=3.10, but its
code and all deps compile and run on 3.9 (verified), so 3.9 is the real floor. If
we are launched under something older still, we re-exec under a newer interpreter
when one is available, and otherwise exit with a clear message rather than a deep
ImportError/SyntaxError.
"""
import os
import sys

_MIN = (3, 9)


def _ensure_modern_python():
    if sys.version_info >= _MIN:
        return
    import shutil

    for candidate in ("python3.13", "python3.12", "python3.11", "python3.10", "python3.9"):
        path = shutil.which(candidate)
        if path:
            os.execv(path, [path, os.path.abspath(__file__), *sys.argv[1:]])
    sys.exit(
        "diffbot db requires Python >= {}.{}, but {}.{} was found and no newer "
        "interpreter is on PATH. Install Python {}.{}+ and retry.".format(
            *_MIN, sys.version_info[0], sys.version_info[1], *_MIN
        )
    )


_ensure_modern_python()

_VENDOR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _VENDOR not in sys.path:
    sys.path.insert(0, _VENDOR)

from diffbot.cli import main

if __name__ == "__main__":
    sys.exit(main())
