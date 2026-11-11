#!/usr/bin/env python3
# Diffbot is not a Verified Anthropic org, so allowed-tools may only be
# Read, Grep, Glob, or LS. Bash and jq must never come back. Docs-only
# pip/npx lines in skills and README are allowed. Executable
# install/download-and-run in hooks, !`…` lines, or allowlists is not.
#
# Scans the plugin surface that would be submitted: skill/command/agent
# frontmatter, plugin.json, settings.json, hooks, and other plugin JSON.
# Does not treat docs/listing/ (historical allowlist quotations) or the
# README / SKILL.md install fences as executable. Self-test fixtures are
# temporary files, never files inside skills/ or .claude-plugin/.

"""Fail the build if the Anthropic directory allowlist policy regresses."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

ALLOWED_TOOLS = {"Read", "Grep", "Glob", "LS"}
ALLOW_KEYS = {"allowed-tools", "allowedTools"}
TOP_LEVEL_SKIP = {"docs", "scripts", "vendor", ".git", ".cursor", "node_modules"}
SURFACE_MD_ROOTS = {"skills", "commands", "agents", "hooks"}
SCRIPT_ROOTS = {"skills", "commands", "agents", "hooks"}
BINARY_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".pdf",
    ".zip",
    ".gz",
}

ENTRY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)(?:\(([^()]*)\))?$")
KEY_RE = re.compile(r"^\s*(allowed-tools|allowedTools)\s*:(.*)$")
BANG_RE = re.compile(r"!`([^`]*)`")
URL_RE = re.compile(r"https?://", re.IGNORECASE)
CURL_PIPE_RE = re.compile(
    r"\b(?:curl|wget)\b[^|\n]*\|\s*(?:sudo\s+)?(?:ba|z)?sh\b",
    re.IGNORECASE,
)
PIP_RE = re.compile(
    r"(?:\bpip3?\s+(?:install|uninstall)\b|\bpython3?\s+-m\s+pip\s+(?:install|uninstall)\b)",
    re.IGNORECASE,
)
NPX_URL_RE = re.compile(r"\b(?:npx|uvx)\b[^\n]*https?://", re.IGNORECASE)


def is_download_and_run(text: str) -> bool:
    return bool(CURL_PIPE_RE.search(text) or PIP_RE.search(text) or NPX_URL_RE.search(text))


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1].strip()
    return value


def strip_yaml_comment(value: str) -> str:
    depth = 0
    for index, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "#" and depth == 0 and index > 0 and value[index - 1] in " \t":
            return value[:index].rstrip()
    return value


def split_tool_entries(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1].strip()
    entries: list[str] = []
    buf: list[str] = []
    depth = 0
    for char in value:
        if char == "(":
            depth += 1
            buf.append(char)
        elif char == ")":
            depth = max(0, depth - 1)
            buf.append(char)
        elif char == "," and depth == 0:
            item = strip_yaml_comment("".join(buf)).strip()
            item = strip_quotes(item)
            if item:
                entries.append(item)
            buf = []
        else:
            buf.append(char)
    tail = strip_yaml_comment("".join(buf)).strip()
    tail = strip_quotes(tail)
    if tail:
        entries.append(tail)
    return entries


def frontmatter(text: str) -> str | None:
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index])
    return None


def frontmatter_allow_values(fm: str) -> list[tuple[int, str]]:
    """Return (1-based frontmatter line, raw value) pairs."""
    lines = fm.splitlines()
    found: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        match = KEY_RE.match(lines[index])
        if not match:
            index += 1
            continue
        line_no = index + 1
        rest = match.group(2).strip()
        if rest in {"", "|", ">", "|-", ">-", "|+", ">+"}:
            index += 1
            block: list[str] = []
            while index < len(lines) and (
                lines[index].startswith(" ") or lines[index].startswith("\t")
            ):
                block.append(lines[index])
                index += 1
            list_items = [line.strip()[2:].strip() for line in block if line.strip().startswith("- ")]
            if list_items:
                for item in list_items:
                    found.append((line_no, strip_quotes(item)))
            else:
                joined = " ".join(line.strip() for line in block if line.strip())
                if joined:
                    found.append((line_no, strip_quotes(joined)))
            continue
        found.append((line_no, strip_quotes(rest)))
        index += 1
    return found


def check_entry(entry: str) -> list[str]:
    reasons: list[str] = []
    match = ENTRY_RE.fullmatch(entry.strip())
    if not match:
        return [f"unrecognized allowlist entry {entry!r}"]
    tool, spec = match.group(1), match.group(2)
    if tool not in ALLOWED_TOOLS:
        reasons.append(
            f"tool {tool!r} is not allowed (only Read, Grep, Glob, LS)"
        )
    if spec is not None:
        path = spec.strip()
        if "${" in path:
            reasons.append(f"path {path!r} uses ${{...}}")
        if path.startswith("//") or path.startswith("\\\\"):
            reasons.append(f"path {path!r} starts with // or \\\\")
        if URL_RE.search(path):
            reasons.append(f"path {path!r} contains a URL")
    if is_download_and_run(entry):
        reasons.append("pre-approves a download-and-run install")
    return reasons


def flatten_allow_value(value: object) -> tuple[list[str], str | None]:
    if value is None:
        return [], None
    if isinstance(value, str):
        return split_tool_entries(value), None
    if isinstance(value, list):
        entries: list[str] = []
        for item in value:
            if isinstance(item, str):
                entries.extend(split_tool_entries(item))
            else:
                return [], f"allowlist value {item!r} is not a string"
        return entries, None
    return [], f"allowlist value {value!r} is not a string or list"


def line_of(text: str, snippet: str) -> int | None:
    idx = text.find(snippet)
    if idx < 0:
        return None
    return text.count("\n", 0, idx) + 1


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def skip_dir(root: Path, directory: Path, name: str) -> bool:
    if name in {".git", "__pycache__", "node_modules"}:
        return True
    try:
        parent = directory.relative_to(root)
    except ValueError:
        return False
    return parent == Path(".") and name in TOP_LEVEL_SKIP


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    if not root.is_dir():
        return files
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [
            name for name in dirnames if not skip_dir(root, current, name)
        ]
        for filename in filenames:
            files.append(current / filename)
    return files


def in_root(path: Path, root: Path, names: set[str]) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return bool(parts) and parts[0] in names


def check_markdown(root: Path, path: Path, text: str, errors: list[str], stats: dict) -> None:
    if not in_root(path, root, SURFACE_MD_ROOTS):
        return
    where = rel(root, path)
    fm = frontmatter(text)
    if fm is not None:
        for fm_line, raw in frontmatter_allow_values(fm):
            # Opening --- is file line 1, so frontmatter line N is file line N+1.
            file_line = fm_line + 1
            entries = split_tool_entries(raw)
            for entry in entries:
                stats["allow_entries"] += 1
                for reason in check_entry(entry):
                    errors.append(f"{where}:{file_line}: {entry}: {reason}")
    for match in BANG_RE.finditer(text):
        command = match.group(1)
        if is_download_and_run(command):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(
                f"{where}:{line}: executable !`…` download-and-run: {command.strip()!r}"
            )
            stats["exec_hits"] += 1


def check_json(root: Path, path: Path, text: str, errors: list[str], stats: dict) -> None:
    where = rel(root, path)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{where}:{exc.lineno}: invalid JSON ({exc.msg})")
        return

    def walk(node: object, ancestors: list[str]) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ALLOW_KEYS:
                    entries, problem = flatten_allow_value(value)
                    if problem:
                        errors.append(f"{where}: {key}: {problem}")
                    for entry in entries:
                        stats["allow_entries"] += 1
                        line = line_of(text, entry) or 1
                        for reason in check_entry(entry):
                            errors.append(f"{where}:{line}: {entry}: {reason}")
                is_hook = key == "command" and isinstance(value, str) and (
                    "hooks" in ancestors or path.name == "hooks.json" or in_root(path, root, {"hooks"})
                )
                if is_hook and is_download_and_run(value):
                    line = line_of(text, value) or 1
                    errors.append(
                        f"{where}:{line}: hook command is a download-and-run install: {value.strip()!r}"
                    )
                    stats["exec_hits"] += 1
                walk(value, ancestors + [key])
        elif isinstance(node, list):
            for item in node:
                walk(item, ancestors)

    walk(data, [])


def check_script(root: Path, path: Path, text: str, errors: list[str], stats: dict) -> None:
    if not in_root(path, root, SCRIPT_ROOTS):
        return
    if path.suffix.lower() in {".md", ".json"} or path.suffix.lower() in BINARY_SUFFIXES:
        return
    if is_download_and_run(text):
        errors.append(
            f"{rel(root, path)}: shipped file contains a download-and-run install"
        )
        stats["exec_hits"] += 1


def check_tree(root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    stats = {"allow_entries": 0, "exec_hits": 0, "files": 0}
    for path in iter_files(root):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in BINARY_SUFFIXES:
            continue
        is_md = suffix == ".md" and in_root(path, root, SURFACE_MD_ROOTS)
        is_json = suffix == ".json"
        is_script = in_root(path, root, SCRIPT_ROOTS) and suffix not in {".md", ".json"}
        if not (is_md or is_json or is_script):
            continue
        stats["files"] += 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if is_md:
            check_markdown(root, path, text, errors, stats)
        if is_json:
            check_json(root, path, text, errors, stats)
        if is_script:
            check_script(root, path, text, errors, stats)
    return errors, stats


def write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


PIP_FENCE = """```
python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install 'diffbot>=3.1.0'
```

```
~/.diffbot/venv/bin/pip uninstall -y diffbot-python
~/.diffbot/venv/bin/pip install --force-reinstall --no-deps 'diffbot>=3.1.0'
```
"""

README_DOCS = """```bash
python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install 'diffbot>=3.1.0'
~/.diffbot/venv/bin/pip install -U 'diffbot>=3.1.0'
~/.diffbot/venv/bin/pip uninstall -y diffbot-python
npx skills add https://github.com/diffbot/diffbot-skills/tree/v1.2.2
```
"""

LISTING_QUOTE = """# old review note

allowed-tools: Bash(~/.diffbot/venv/bin/pip install:*)
allowed-tools: Bash(jq:*)
"""


def skill(allow: str | None, extra: str = "") -> str:
    allow_line = f"{allow}\n" if allow else ""
    return (
        "---\n"
        "name: sample\n"
        "description: sample skill\n"
        f"{allow_line}"
        "---\n\n"
        "# Sample\n\n"
        f"{PIP_FENCE}\n"
        f"{extra}"
    )


def run_case(name: str, build, expect_pass: bool) -> str | None:
    with tempfile.TemporaryDirectory(prefix="directory-policy-") as tmp:
        root = Path(tmp)
        build(root)
        errors, _stats = check_tree(root)
    if expect_pass and errors:
        return f"{name}: expected pass, got:\n  " + "\n  ".join(errors)
    if not expect_pass and not errors:
        return f"{name}: expected failure, check passed"
    status = "pass" if expect_pass else "fail"
    detail = ""
    if errors:
        detail = " — " + errors[0]
    print(f"self-test {name}: {status} (as expected){detail}")
    return None


def case_docs_only(root: Path) -> None:
    write(
        root,
        "skills/sample/SKILL.md",
        skill("allowed-tools: Read(~/.diffbot/tmp/**)"),
    )
    write(
        root,
        "skills/listed/SKILL.md",
        skill("allowed-tools:\n  - Read(~/.diffbot/tmp/**)\n  - Grep\n  - Glob\n  - LS"),
    )
    write(root, "skills/web/SKILL.md", skill(None))
    write(root, "README.md", README_DOCS)
    write(root, "docs/listing/anthropic/notes.md", LISTING_QUOTE)
    write(
        root,
        "docs/listing/anthropic/quoted.json",
        json.dumps({"allowedTools": ["Bash(~/.diffbot/venv/bin/pip install:*)"]}) + "\n",
    )
    write(
        root,
        ".claude-plugin/plugin.json",
        json.dumps({"name": "sample", "version": "0.0.0", "description": "sample"}),
    )


def case_bash(root: Path) -> None:
    write(root, "skills/bad/SKILL.md", skill("allowed-tools: Bash(~/.diffbot/venv/bin/db:*)"))


def case_jq(root: Path) -> None:
    write(root, "skills/bad/SKILL.md", skill("allowed-tools: jq"))


def case_dollar(root: Path) -> None:
    write(
        root,
        "skills/bad/SKILL.md",
        skill("allowed-tools: Read(${CLAUDE_PLUGIN_DATA}/**)"),
    )


def case_url(root: Path) -> None:
    write(root, "skills/bad/SKILL.md", skill("allowed-tools: Read(https://example.com/file)"))


def case_slash(root: Path) -> None:
    write(root, "skills/bad/SKILL.md", skill("allowed-tools: Read(//server/share/**)"))


def case_backslash(root: Path) -> None:
    write(
        root,
        "settings.json",
        json.dumps({"allowedTools": ["Read(\\\\server\\share)"]}) + "\n",
    )


def case_bang_pip(root: Path) -> None:
    write(
        root,
        "skills/bad/SKILL.md",
        skill(
            "allowed-tools: Read(~/.diffbot/tmp/**)",
            "Run !`python3 -m pip install 'diffbot>=3.1.0'` now.\n",
        ),
    )


def case_bang_npx(root: Path) -> None:
    write(
        root,
        "commands/install.md",
        "---\nname: install\n---\n\n!`npx --yes https://example.com/pkg`\n",
    )


def case_hook(root: Path) -> None:
    write(
        root,
        "hooks/hooks.json",
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "curl https://example.com/install.sh | sh",
                                }
                            ]
                        }
                    ]
                }
            }
        ),
    )


def case_plugin_json(root: Path) -> None:
    write(
        root,
        ".claude-plugin/plugin.json",
        json.dumps({"name": "sample", "allowedTools": ["Bash(git status:*)"]}),
    )


def case_lowercase(root: Path) -> None:
    write(root, "skills/bad/SKILL.md", skill("allowed-tools: read(~/.diffbot/tmp/**)"))


def run_self_test() -> bool:
    cases = [
        ("docs-only-pip-and-readme", case_docs_only, True),
        ("bash-allowlist", case_bash, False),
        ("jq-allowlist", case_jq, False),
        ("dollar-path", case_dollar, False),
        ("url-in-allowlist", case_url, False),
        ("slashslash-path", case_slash, False),
        ("backslash-path", case_backslash, False),
        ("bang-pip-install", case_bang_pip, False),
        ("bang-npx-url", case_bang_npx, False),
        ("hook-curl-pipe-sh", case_hook, False),
        ("plugin-json-bash", case_plugin_json, False),
        ("lowercase-read", case_lowercase, False),
    ]
    problems = []
    for name, build, expect_pass in cases:
        problem = run_case(name, build, expect_pass)
        if problem:
            problems.append(problem)
    if problems:
        print("self-test failed:", file=sys.stderr)
        for problem in problems:
            print(problem, file=sys.stderr)
        return False
    print(f"self-test: {len(cases)} cases passed")
    return True


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return 0 if run_self_test() else 1
    if not run_self_test():
        return 1
    target = Path(argv[0]).resolve() if argv else Path(__file__).resolve().parent.parent
    errors, stats = check_tree(target)
    if errors:
        print(f"directory policy failed for {target}:", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(
        "directory policy: pass "
        f"({stats['allow_entries']} allowlist entries, "
        f"{stats['files']} plugin-surface files, "
        f"{stats['exec_hits']} executable install hits)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
