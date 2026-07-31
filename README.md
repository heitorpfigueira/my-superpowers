# my-superpowers

A personal set of Claude Code skills implementing a structured software-development
workflow: brainstorm a design, get it approved, write a plan, implement it with
strict TDD, review it, and land it.

This is a trimmed-down, personal fork of the skill content from
[obra/superpowers](https://github.com/obra/superpowers) (MIT licensed). It keeps
the methodology — the individual skills — and drops everything that only makes
sense for a distributed plugin: the marketplace manifests, per-harness adapters
(Codex/Cursor/Gemini/OpenCode/Pi/etc.), install hooks, telemetry, the visual
brainstorming companion server, and the contributor rules for the upstream repo.

## The workflow

1. **brainstorming** — before any code, refines a rough idea into a design
   through one-question-at-a-time dialogue, then writes a spec doc for approval.
2. **using-git-worktrees** — sets up an isolated branch/workspace and verifies a
   clean test baseline.
3. **writing-plans** — breaks an approved design into small (2-5 min) tasks with
   exact file paths and verification steps.
4. **subagent-driven-development** (or **executing-plans** if you don't have
   subagent access) — implements the plan task-by-task with review checkpoints.
5. **test-driven-development** — RED-GREEN-REFACTOR, enforced. Code written
   before its test gets deleted.
6. **requesting-code-review** / **receiving-code-review** — review against the
   plan, severity-ranked issues, structured response to feedback.
7. **finishing-a-development-branch** — merge/PR/keep/discard decision and
   worktree cleanup.

Supporting skills: **systematic-debugging** (4-phase root-cause process),
**verification-before-completion**, **dispatching-parallel-agents**, and
**writing-skills** (a meta-skill for authoring/editing skills, TDD-style, if you
want to extend this set yourself).

See `skills/using-superpowers/SKILL.md` for the bootstrap rule that makes these
skills trigger automatically instead of sitting unused on disk.

## Using this with Claude Code

There's no plugin/marketplace wrapper here — just skills. Claude Code discovers
skills placed in `~/.claude/skills/`. To make them available in every project:

```bash
cp -r skills/* ~/.claude/skills/
```

(Or symlink individual skill directories if you'd rather manage updates from
this repo directly.)

Once installed, skills trigger based on their `description:` frontmatter and
the rules in `using-superpowers/SKILL.md` — no explicit invocation needed,
though you can also request one by name (e.g. "use the brainstorming skill").

## License

MIT — see LICENSE. Skill content originally from
[obra/superpowers](https://github.com/obra/superpowers), by Jesse Vincent /
Prime Radiant.
