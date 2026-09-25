# my-superpowers

A personal set of **Claude Code and Codex** skills implementing a structured software-development
workflow: open a three-tier branch structure, brainstorm a design, get it approved,
write a plan, implement it with strict TDD across small local branches, review it,
report on it, and land it through Pull Requests.

This started as a trimmed-down personal fork of the skill content from
[obra/superpowers](https://github.com/obra/superpowers) (MIT licensed). It has its own
branch model, document layout, and reporting step. Claude and Codex now share the
same workflow, with small references translating tool names, skill discovery,
worker dispatch, local state, and shell commands for each host. There is no
marketplace wrapper, automatic install hook, or bundled model service.

The adaptation preserves branching, TDD, independent reviews, fix limits, and
human approval gates. Host permissions and explicit user instructions take
precedence. See the [host contract](skills/using-superpowers/references/platforms.md),
[Claude reference](skills/using-superpowers/references/claude-code.md), and
[Codex reference](skills/using-superpowers/references/codex.md).

## The workflow

Before any of these: **coordinator** (optional) routes an incoming task to the right
skill or MCP server in the first place — it isn't part of the numbered sequence
below, it decides whether to start the sequence at all. See
`skills/coordinator/SKILL.md`; it builds and maintains its own local registry of
what else is installed the first time you use it, rather than shipping one that
would only be accurate for one machine.

1. **git-branch-workflow** — the entry point for any requested unit of work.
   Opens (or reuses) a `release`/`patch` grandparent branch and a
   `feature`/`bugfix`/`documentation` parent branch under it, then drives the
   rest of this list from inside that structure.
2. **brainstorming** — refines a rough idea into a design through
   one-question-at-a-time dialogue (plus scope/research/impact/architecture/UI-UX
   exploration where relevant), then writes a spec doc for approval. Saved to
   `docs/development/spec/`.
3. **writing-plans** — breaks the approved spec into small (2-5 min) tasks, one
   child branch per task, with exact file paths, behavior-and-intent framing, and
   verification steps. Saved to `docs/development/plan/`.
4. **subagent-driven-development** (or **executing-plans** if you don't have
   subagent access) — implements the plan task-by-task, one child branch at a
   time, with review checkpoints.
5. **test-driven-development** — RED-GREEN-REFACTOR, enforced, testing the
   system's behavior and intent rather than its implementation. Code written
   before its test gets deleted.
6. **requesting-code-review** / **receiving-code-review** — review against the
   plan before a child branch squash-merges into its parent.
7. **writing-documentation** — captures living reference docs (glossary,
   architecture, technology, features, coding conventions) as they come up,
   in `docs/`.
8. **writing-development-report** — once every child branch under a parent is
   merged, summarizes everything built and every decision made, saved to
   `docs/development/report/`.
9. **finishing-a-development-branch** — opens the Pull Request that lands a
   parent branch on its grandparent, or a grandparent on `main`.

Supporting skills: **using-git-worktrees** (optional filesystem isolation, used
on top of or independently of the branch tiers), **systematic-debugging**
(4-phase root-cause process), **verification-before-completion**,
**dispatching-parallel-agents**, and **writing-skills** (a meta-skill for
authoring/editing skills, TDD-style, if you want to extend this set yourself).

See [using-superpowers](skills/using-superpowers/SKILL.md) for discovery rules and
the activation step below for making those rules available to the host.

## Installation for either host

Install **Python 3.10+** and **Git**, then run these commands from this repository.
Use `python3` instead of `python` where that is your Python 3 command. These examples
work in PowerShell or Bash. Start with a read-only preview for your chosen host:

```text
python tools/install.py --target codex
python tools/install.py --target claude
```

To install, repeat the chosen command with `--apply`:

```text
python tools/install.py --target codex --apply
python tools/install.py --target claude --apply
```

You can install both. Each command copies the complete skill set, including shared
references, prompt templates, and helpers. Keep the set together: individual skills
depend on those references and on other skills in the workflow.

| Host | Default skills directory | Default local state directory |
|---|---|---|
| Claude Code | `<CLAUDE_CONFIG_DIR or ~/.claude>/skills` | `<CLAUDE_CONFIG_DIR or ~/.claude>/my-superpowers` |
| Codex | `~/.agents/skills` | `<CODEX_HOME or ~/.codex>/my-superpowers` |

Codex's `CODEX_HOME` changes its default state/instruction location; it does not
change this installer's default skills directory. A managed Codex app or profile
may expose a different skill root. Use the root advertised by that session:

```text
python tools/install.py --target codex --skills-dir "C:/path/to/profile/skills" --state-dir "C:/path/to/profile/my-superpowers"
```

Inspect the preview, then add `--apply`. `--skills-dir` and `--state-dir` work for
either host and accept absolute paths containing spaces. State must be outside the
skills directory. Keep separate state directories for different hosts/profiles.
For the installer, use `--state-dir` for an override; `MY_SUPERPOWERS_STATE_DIR` is
an optional runtime fallback when no explicit activation path is supplied.

The installer refuses to overwrite an unmanaged skill directory, including a
manually copied `coordinator`. Preserve or relocate that copy before retrying.
It also refuses updates over locally edited managed files. It preserves unrelated
skills, custom files, and the coordinator registry; it never edits host settings
or existing instruction files.

### Activate the workflow

After installation, open `bootstrap.md` in the printed state directory. Merge its
marked block into your active host instructions while preserving existing content:

- Claude Code: your active `CLAUDE.md`, normally under `CLAUDE_CONFIG_DIR` or `~/.claude`.
- Codex: your active `AGENTS.md`, normally under `CODEX_HOME` or `~/.codex`. An
  `AGENTS.override.md` at the same level takes precedence; use the file that actually
  governs the session. Respect applicable project instructions as well.

The block records the installed paths, routes new tasks through coordinator first,
and then uses using-superpowers for discovery. It respects fast-path reads and a
user's opt-out. This is an explicit activation step; copying the files alone does
not guarantee that the host loads the bootstrap rules.

Start a fresh session and inspect its skill catalog. You can request a skill by
name, for example "use the brainstorming skill." The host controls discovery and
invocation; Codex should read the exact installed `SKILL.md` when no native skill
loader is exposed. Do not treat another host's cached tools as available.

The coordinator creates or refreshes `coordinator-registry.md` in the resolved
state directory during its normal authorized discovery. This machine-specific
cache stays outside the repository and installed skills. Existing Claude registry
entries must be revalidated before migration; they are not Codex tool bindings.

### Updates

Update this checkout, then rerun the same preview and `--apply` command, retaining
any path overrides. The installer uses `install.json` in the state directory to
identify the files it owns, compare hashes, and remove unchanged files that the
updated package no longer contains. Keep that manifest with its installation.
Changes in the generated bootstrap block must be merged into active instructions
manually. Put your custom instruction text outside the generated block.

Preflight failures leave installed files unchanged. An interrupted copy or an OS
write failure can leave a partial installation: inspect and reconcile it before
retrying. The installer deliberately does not adopt untracked files or silently
overwrite local edits, and it does not provide a force-overwrite option.

## Runtime requirements and limits

The SDD artifact commands share a portable Python implementation; existing Bash
entry points remain available. In PowerShell, call `sdd.py` directly. See
[shells.md](skills/using-superpowers/references/shells.md) for commands and cleanup.
Optional tools retain their own requirements: the test-polluter diagnostic uses
Bash/npm, graph rendering uses Node.js/Graphviz, and PR steps need the relevant
GitHub CLI/repository access. Git snippets written in Bash must be translated
when the active shell is PowerShell.

Worker creation, messaging, nesting, capacity, model selection, and worktree
permissions depend on the current host session. Resolve them from its exposed
tools. When parallel execution is unavailable, serialize work while preserving
the same review and approval gates. If an independent reviewer or a required
capability cannot be supplied, prepare the artifacts and report that blocker.

## Checking these changes

Run the focused mechanics tests from the repository:

```text
python -B -m unittest discover -s tests -v
git diff --check
```

The tests use temporary directories and Git fixtures. They check preview/install
and update behavior, ownership/collision handling, profile paths, installed files
and references, task extraction, commit-range review artifacts, legacy ledger
adoption, path boundaries, and plan-specific cleanup. Bash launcher checks use
Git Bash on Windows or Bash on Unix; set `SUPERPOWERS_TEST_BASH` to select another
Bash executable. They are skipped when Bash is unavailable.

These checks do not invoke an agent, run skill scenarios, or evaluate whether a
model follows the workflow. Validation for this adaptation ran on Windows with
Python and Git Bash; macOS/Linux execution has not been verified. Historical
development documents describe earlier states; the host references above describe
the current platform contract.

## License

MIT — see LICENSE. Skill content originally from
[obra/superpowers](https://github.com/obra/superpowers), by Jesse Vincent /
Prime Radiant.
