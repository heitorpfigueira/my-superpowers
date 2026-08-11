# my-superpowers

A personal set of Claude Code skills implementing a structured software-development
workflow: open a three-tier branch structure, brainstorm a design, get it approved,
write a plan, implement it with strict TDD across small local branches, review it,
report on it, and land it through Pull Requests.

This started as a trimmed-down personal fork of the skill content from
[obra/superpowers](https://github.com/obra/superpowers) (MIT licensed), dropping
everything that only makes sense for a distributed plugin (marketplace manifests,
per-harness adapters, install hooks, telemetry, the visual brainstorming companion
server, upstream contributor rules), and has since diverged with its own branch
model, doc layout, and reporting step layered on top of the upstream methodology.

## The workflow

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
