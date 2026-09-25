#!/usr/bin/env python3
"""Install shared skills for Claude Code or Codex. Defaults to a read-only preview."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def destinations(target, home=None, environ=None):
    home = Path.home() if home is None else Path(home)
    environ = os.environ if environ is None else environ
    if target == "claude":
        host_home = Path(environ.get("CLAUDE_CONFIG_DIR") or home / ".claude").expanduser()
        return host_home / "skills", host_home / "my-superpowers", host_home / "CLAUDE.md"
    host_home = Path(environ.get("CODEX_HOME") or home / ".codex").expanduser()
    return home / ".agents" / "skills", host_home / "my-superpowers", host_home / "AGENTS.md"


def overlaps(a, b):
    return a.is_relative_to(b) or b.is_relative_to(a)


def safe_path(root, relative):
    key = PurePosixPath(relative)
    if (not relative or "\\" in relative or key.is_absolute() or PureWindowsPath(relative).drive
            or ".." in key.parts or key.as_posix() != relative):
        raise ValueError(f"invalid managed path: {relative!r}")
    path = root.joinpath(*key.parts)
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"managed path escapes destination: {relative}")
    current = path
    while current != root:
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError(f"redirected managed path: {current}")
        if current != path and current.exists() and not current.is_dir():
            raise ValueError(f"managed path parent is not a directory: {current}")
        current = current.parent
    if root.exists() and not root.is_dir():
        raise ValueError(f"destination is not a directory: {root}")
    return path


def install(source, target, skills_dir, state_dir, apply=False):
    source = (source / "skills").resolve()
    skills_dir = skills_dir.expanduser().resolve()
    state_dir = state_dir.expanduser().resolve()
    if overlaps(source, skills_dir) or overlaps(source, state_dir):
        raise ValueError("source and installation/state paths must be separate")
    if overlaps(state_dir, skills_dir):
        raise ValueError("state directory must live outside the skills installation")
    if not source.is_dir():
        raise ValueError(f"missing source skills directory: {source}")
    files = {}
    for skill in sorted(source.iterdir()):
        if not skill.is_dir() or not (skill / "SKILL.md").is_file():
            continue
        for path in sorted(skill.rglob("*")):
            relative = path.relative_to(source).as_posix()
            safe_path(source, relative)
            if "__pycache__" in path.parts or path.suffix == ".pyc" or not path.is_file():
                continue
            files[relative] = digest(path)
    if not files:
        raise ValueError("source contains no skills")
    manifest_path = safe_path(state_dir, "install.json")
    bootstrap_path = safe_path(state_dir, "bootstrap.md")
    temporary = safe_path(state_dir, "install.json.tmp")
    if temporary.exists():
        raise ValueError(f"unfinished manifest write; inspect before retrying: {temporary}")
    previous = {}
    old_manifest = None
    if manifest_path.exists():
        old_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (not isinstance(old_manifest, dict)
                or old_manifest.get("version") != 1 or old_manifest.get("target") != target
                or old_manifest.get("skills_dir") != str(skills_dir)
                or not isinstance(old_manifest.get("files"), dict)):
            raise ValueError("installation manifest does not match this target/destination")
        previous = old_manifest["files"]
    # Complete preflight before any directory or file is changed.
    for relative in set(files) | set(previous):
        path = safe_path(skills_dir, relative)
        if relative in previous:
            if path.exists() and (not path.is_file() or digest(path) != previous[relative]):
                raise ValueError(f"locally modified managed file; preserve or reconcile it first: {path}")
        elif path.exists():
            raise ValueError(f"unmanaged file collision; preserve or relocate it first: {path}")
        top = relative.split("/", 1)[0]
        if (skills_dir / top).exists() and not any(key.startswith(top + "/") for key in previous):
            raise ValueError(f"unmanaged skill directory collision: {skills_dir / top}")
    if bootstrap_path.exists():
        expected = old_manifest.get("bootstrap_hash") if old_manifest else None
        if not expected or digest(bootstrap_path) != expected:
            raise ValueError(f"locally modified or unmanaged bootstrap: {bootstrap_path}")
    added = sorted(set(files) - set(previous))
    changed = sorted(key for key in set(files) & set(previous)
                     if files[key] != previous[key] or not (skills_dir / key).exists())
    removed = sorted(set(previous) - set(files))
    print(f"{'Apply' if apply else 'Preview'} {target}: {len(added)} add, {len(changed)} update, {len(removed)} remove")
    print(f"Skills: {skills_dir}\nState: {state_dir}")
    if not apply:
        print("No files changed. Add --apply to install. Existing instructions are never edited.")
        return
    skills_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    # On an interrupted install, reconcile partial files before retrying; never adopt
    # or overwrite an untracked file merely because its bytes happen to match.
    for relative in added + changed:
        path = safe_path(skills_dir, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, path)
    for relative in removed:
        safe_path(skills_dir, relative).unlink(missing_ok=True)
    bootstrap = ("# my-superpowers activation\n\n"
                 "Add the following block to your active host instructions, preserving existing content.\n"
                 "For Claude use CLAUDE.md; for Codex use the active AGENTS.md (or its override).\n\n"
                 "<!-- my-superpowers:start -->\n"
                 "Use my-superpowers for software-development work when the user has not opted out.\n"
                 f"Installed skills: `{skills_dir}`. Host: `{target}`.\n"
                 f"Local state directory: `{state_dir}`.\n"
                 f"Read `{skills_dir / 'using-superpowers' / 'references' / 'platforms.md'}` "
                 "for the host mapping before tool operations.\n"
                 "For task routing, consult coordinator first; respect its fast path. "
                 "Then follow using-superpowers for skill discovery and the selected workflow.\n"
                 "User instructions and host restrictions take precedence. "
                 "Retain my-superpowers' existing human review and approval gates.\n"
                 "<!-- my-superpowers:end -->\n")
    bootstrap_path.write_text(bootstrap, encoding="utf-8", newline="\n")
    manifest = {"version": 1, "target": target, "skills_dir": str(skills_dir),
                "files": files, "bootstrap_hash": digest(bootstrap_path)}
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(manifest_path)
    print(f"Installed. Activation instructions: {bootstrap_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("claude", "codex"), required=True)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skills-dir", type=Path)
    parser.add_argument("--state-dir", type=Path)
    parser.add_argument("--apply", action="store_true", help="write after all collision checks pass")
    args = parser.parse_args()
    skills, state, _ = destinations(args.target)
    try:
        install(args.source, args.target, args.skills_dir or skills, args.state_dir or state, args.apply)
    except (OSError, ValueError, TypeError) as error:
        print(f"install: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
