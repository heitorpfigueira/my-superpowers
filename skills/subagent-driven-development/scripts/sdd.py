#!/usr/bin/env python3
"""Portable SDD artifacts. Run from the task's repository/worktree (Python 3.10+)."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys


def git(*args):
    result = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise ValueError(result.stderr.strip() or "git command failed")
    return result.stdout.rstrip("\n")


def checked_child(root, path):
    """Reject redirected paths before creating, replacing, or removing artifacts."""
    if not path.is_relative_to(root) or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"artifact path escapes repository: {path}")
    current = path
    while current != root:
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError(f"redirected artifact path: {current}")
        current = current.parent
    return path


def workspace(plan, create=True):
    plan = Path(plan).resolve(strict=True)
    if not plan.is_file():
        raise ValueError(f"not a plan file: {plan}")
    root = Path(git("rev-parse", "--show-toplevel")).resolve()
    if not plan.is_relative_to(root):
        raise ValueError("plan file must be inside the current repository/worktree")
    slug = plan.stem
    if not slug or slug in (".", ".."):
        raise ValueError("cannot derive a workspace name from this plan")
    base = checked_child(root, root / ".superpowers" / "sdd")
    directory = checked_child(root, base / slug)
    identity = checked_child(root, directory / ".plan-path")
    plan_key = plan.relative_to(root).as_posix()
    if identity.exists() and identity.read_text(encoding="utf-8").strip() != plan_key:
        raise ValueError(f"workspace belongs to a different plan: {directory}")
    if directory.exists() and not identity.exists() and any(directory.iterdir()):
        # Existing Bash-era ledgers can be adopted only when their identity agrees.
        ledger = checked_child(root, directory / "progress.md")
        first = ledger.read_text(encoding="utf-8").splitlines()[0] if ledger.is_file() and ledger.stat().st_size else ""
        prefix = "# SDD ledger — plan: "
        old_plan = Path(first[len(prefix):]) if first.startswith(prefix) else None
        if old_plan is None or (root / old_plan).resolve() != plan:
            raise ValueError(f"unidentified workspace or different plan; inspect its ledger: {directory}")
    if create:
        directory.mkdir(parents=True, exist_ok=True)
        ignore = checked_child(root, base / ".gitignore")
        old = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
        if "*" not in old.splitlines():
            ignore.write_text(old + ("\n" if old and not old.endswith("\n") else "") + "*\n", encoding="utf-8")
        identity.write_text(plan_key + "\n", encoding="utf-8")
    return directory


def task_text(plan, number):
    if number < 1:
        raise ValueError("task number must be positive")
    lines = Path(plan).read_text(encoding="utf-8-sig").splitlines(keepends=True)
    selected = []
    active = False
    fence = None
    for line in lines:
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        else:
            heading = re.match(r"^ {0,3}#{1,6}\s+Task\s+(\d+)(?:\D|$)", line)
            if heading:
                if active:
                    break
                active = int(heading[1]) == number
        if active:
            selected.append(line)
    if not selected:
        raise ValueError(f"task {number} not found in {plan}")
    return "".join(selected)


def write_output(path, content):
    root = Path(git("rev-parse", "--show-toplevel")).resolve()
    path = checked_child(root, Path(path).absolute())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("workspace", "brief", "review", "clean"):
        command = commands.add_parser(name)
        command.add_argument("plan", type=Path)
        if name == "brief":
            command.add_argument("number", type=int)
        if name == "review":
            command.add_argument("base")
            command.add_argument("head")
        if name in ("brief", "review"):
            command.add_argument("outfile", type=Path, nargs="?")
    args = parser.parse_args()
    try:
        if args.command == "workspace":
            print(workspace(args.plan))
        elif args.command == "brief":
            content = task_text(args.plan, args.number)
            directory = workspace(args.plan)
            write_output(args.outfile or directory / f"task-{args.number}-brief.md", content)
        elif args.command == "review":
            base = git("rev-parse", "--verify", "--end-of-options", args.base + "^{commit}")
            head = git("rev-parse", "--verify", "--end-of-options", args.head + "^{commit}")
            revision = f"{base}..{head}"
            content = (f"# Review package: {revision}\n\n## Commits\n"
                       + git("log", "--oneline", revision, "--")
                       + "\n\n## Files changed\n" + git("diff", "--no-ext-diff", "--stat", revision, "--")
                       + "\n\n## Diff\n" + git("diff", "--no-ext-diff", "-U10", revision, "--") + "\n")
            directory = workspace(args.plan)
            write_output(args.outfile or directory / f"review-{base[:7]}..{head[:7]}.diff", content)
        else:
            directory = workspace(args.plan, create=False)
            if directory.exists():
                if not (directory / ".plan-path").exists():
                    raise ValueError("run workspace to validate and adopt this legacy ledger before cleanup")
                shutil.rmtree(directory)
            print(directory)
    except (OSError, ValueError) as error:
        print(f"sdd: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
