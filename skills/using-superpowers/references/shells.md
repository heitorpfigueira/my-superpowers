# Shell and artifact portability

The workflow's Bash examples express Git operations and their ordering. Run them
in Bash, or translate them to the active shell. Do not paste Bash substitutions,
heredocs, `export`, or pipeline syntax into Windows PowerShell.

Use argument arrays for scripts and structured tool fields where available. Quote
paths with spaces. Pass full PR/commit bodies through files rather than shell string
interpolation. In PowerShell, check `$LASTEXITCODE` after native commands and stop
on a failed prerequisite; a later successful command does not erase that failure.
Use the runtime's normal permission mechanism for denied writes; never bypass it.

## SDD helpers

Python 3.10+ and Git are required. From the task worktree, invoke the installed
`subagent-driven-development/scripts/sdd.py` using `python` (or `python3` on systems
where that is the Python 3 command). Each successful command prints its absolute
artifact path on stdout; errors go to stderr with a nonzero exit status.

| Existing Bash entry point | Portable invocation |
|---|---|
| `scripts/sdd-workspace PLAN` | `python /path/to/sdd.py workspace PLAN` |
| `scripts/task-brief PLAN N [OUTFILE]` | `python /path/to/sdd.py brief PLAN N [OUTFILE]` |
| `scripts/review-package PLAN BASE HEAD [OUTFILE]` | `python /path/to/sdd.py review PLAN BASE HEAD [OUTFILE]` |
| Delete this plan's completed workspace | `python /path/to/sdd.py clean PLAN` |

The Bash entry points delegate to the same Python implementation. Invoke a wrapper
with `bash /path/to/script` if the checkout did not preserve its executable bit.
In PowerShell, invoke Python directly. Plan and explicit output files must be inside
the current repository/worktree. Cleanup validates the resolved path and plan
identity before removing only that plan's artifact directory.

The workspace layout stays `.superpowers/sdd/<plan-basename>/`. A `.plan-path`
identity prevents two different plans with the same basename from sharing progress.
An existing workspace is adopted only when its ledger identifies the same plan;
ambiguous artifacts must be inspected, not overwritten. Run `workspace` to validate
an old ledger before cleanup. Preserve the existing workflow's completion gate
before invoking `clean`.

`systematic-debugging/find-polluter.sh` remains an optional Bash/npm diagnostic.
Check for a working Bash installation before using it; otherwise use the documented
manual root-cause investigation. It is not required by the SDD workflow.
Graph rendering uses `node render-graphs.js ...` and optional Graphviz.

## Worktrees and cleanup

Prefer the workspace owner's native tool when available. Record the path and owner
at creation. For raw Git, `git rev-parse --path-format=absolute --git-dir` and
`git rev-parse --path-format=absolute --git-common-dir` avoid shell-specific `cd`
substitutions. Keep the submodule guard and existing branch/review rules.

Use `git worktree remove` for a Git-owned worktree, and the owner's cleanup tool
for a managed workspace. On Windows use native PowerShell file operations with
`-LiteralPath`; resolve and verify a recursive cleanup target first. Never mix
PowerShell path enumeration with `cmd` deletion, or delete a whole scratch root
when the workflow calls for removing one plan's directory.
