# Claude Code and Codex compatibility

The shared skills now resolve host operations through references under
`skills/using-superpowers/references/`. The existing branch tiers, TDD rules,
independent reviews, fix-loop limits, human gates, and reporting workflow remain.
Missing platform capabilities are reported or handled through serial execution
without bypassing those gates.

Coordinator discovery uses the current session catalog and separates local state
by host/profile and project scope. Worker templates use supplied controller IDs,
explicit worktree paths, fresh context, and the host's permitted model choices.

`tools/install.py` previews by default, checks ownership and collisions before
writing, tracks managed files for updates, and generates a separate activation
block. It preserves local registries and unrelated files. It does not edit active
host instructions. The README documents installation, activation, and updates.

The three SDD Bash commands now call a common Python implementation, also usable
directly from PowerShell. It validates artifact paths and plan identity, preserves
legacy ledgers, extracts tasks around fenced examples, includes the full recorded
commit range in reviews, and limits cleanup to the selected plan's workspace.
The Bash launchers verify Python 3.10+ before choosing an interpreter, including
when Windows exposes a nonfunctional Microsoft Store shortcut for `python3`.

## Validation

`python -B -m unittest discover -s tests -v`: **24 checks, 23 passed, one skipped**
on Windows with Python 3.14 and Git Bash. The skipped directory-symlink case
requires a privilege unavailable in this environment. Installer preflight/update
checks, temporary full installs for both hosts, installed metadata/reference
checks, artifact commands, and all three Bash entry points passed.

`git diff --check` passed. Source review covered host-specific substitutions and
preservation of workflow gates. Tests do not invoke agents or evaluate skill
behavior, as requested. macOS/Linux execution and live host discovery/activation
remain unverified. No live skill installation, host configuration edit, or
coordinator registry generation is part of this repository change.
