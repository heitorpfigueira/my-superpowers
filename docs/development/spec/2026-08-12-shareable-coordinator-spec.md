# Shareable Coordinator — Spec

**Created:** 2026-08-12

## Summary

`my-superpowers` ships a set of process skills but no router — nothing that looks at
an incoming task and says which skill or MCP server actually applies. The author's
personal Claude Code setup has one (`~/.claude/skills/coordinator/SKILL.md`), but it's
a single file that mixes two things that don't belong together: general routing logic
that would be useful to anyone, and a hard-coded list of *this machine's* installed
skills, MCP servers, and stack-specific workflow patterns (Expo, React Native, tRPC,
etc.) that would be actively wrong for anyone else's setup.

This spec adds a **shareable coordinator** to the `my-superpowers` repo: a portable
routing skill that ships with the repo's own skill listing built in, and that builds
the rest of its knowledge — what other skills and MCP servers exist on the machine it's
installed on, and what stack a given project is written in — for itself, the first time
it needs to, and keeps that knowledge current as it keeps working.

## Goals

- A `coordinator` skill in the `my-superpowers` repo that anyone can drop into
  `~/.claude/skills/` alongside the rest of the set and get useful routing
  immediately, with zero manual configuration required to make it *work* (though it
  won't yet know about anything outside `my-superpowers` until it's asked to look).
- The skill never needs hand-editing to reflect a new machine's installed skills or
  MCP servers — it discovers and records that itself.
- Updating `my-superpowers` (pulling a new version of the repo, re-copying the skill)
  never wipes out what a given machine has learned about itself.
- The routing logic and the `my-superpowers` skill registry are the only things baked
  in at authoring time. Everything else is inferred per machine, per project.

## Out of scope for this spec

- Migrating the author's own live `~/.claude/skills/coordinator/SKILL.md` onto this
  design. That file keeps working exactly as it does today; adopting the new
  structure for it is a separate, later task.
- Detecting anything beyond skills and MCP servers (custom subagent types, hooks,
  slash commands). Can be added later the same way skills/MCP detection is added now,
  without changing the architecture.
- Any UI beyond conversational prompts — this is a markdown skill file plus a
  markdown data file, nothing renders anywhere else.

## Architecture

Two artifacts with two different lifecycles, never merged into one file:

### 1. `skills/coordinator/SKILL.md` — portable, versioned, identical for everyone

Lives in the `my-superpowers` repo and gets copied to `~/.claude/skills/coordinator/`
the same way every other skill in the set does. Content:

- **Role and precedence** — what a coordinator is for, and that its routing plan wins
  over other skills' own "consult me first" claims, adapted from the personal file's
  existing language but with every machine-specific path (the PowerShell hook
  filename, `~/.augment/...` etc.) removed. Anyone installing this skill wires their
  own trigger for it (a slash command, a session hook, or just invoking it by name);
  this file doesn't assume one.
- **Triage logic** — the fast-path/full-path split that decides whether a request
  needs a full routing plan at all (ported as-is; it's already generic).
- **The `my-superpowers` process skill registry** — the existing table of process /
  execution / integration / meta skills (git-branch-workflow, brainstorming,
  writing-plans, subagent-driven-development, etc.), because this is fixed at
  authoring time: it's always accurate for whatever version of `my-superpowers` shipped
  alongside it. No detection needed for this part — it's static content, like the
  skill descriptions themselves.
- **Self-Setup & Self-Update** — see below. Written at the intent level: *what* the
  registry should contain, *why* it's a separate file, *where* it lives, and *when* to
  touch it. Not a step-by-step scanning algorithm — the coordinator uses its own
  judgment for *how* to read a skill's frontmatter, decide what an MCP server is for,
  or recognize a project's stack, the same way the rest of this workflow trusts
  agent judgment over prescribed scripts elsewhere (see `writing-plans`,
  `systematic-debugging`'s architecture-question step).
- **Stack-adaptation directive** — an explicit instruction that the coordinator should
  notice a project's stack/tech context (dependency manifests, config files, existing
  code) and generate workflow patterns suited to it, rather than only ever offering
  generic, stack-agnostic routing.

Nothing in this file names a specific library, framework, or MCP server. If it can't
be true for an arbitrary Claude Code install, it doesn't belong here.

### 2. `~/.claude/coordinator-registry.md` — generated, local, never versioned

A single file at `~/.claude/`, deliberately **outside** the `skills/coordinator/`
folder so nothing that touches the skill itself (a `my-superpowers` update, a
straight re-copy, a full reinstall of the skill) can ever overwrite it. The
`SKILL.md` core references this path by convention and reads/writes it as needed.

Two kinds of content:

- **Global section** — a skills table and an MCP servers table, covering the whole
  machine. Rebuilt or amended whenever the coordinator learns something new (see
  triggers below). Machine-wide because installed skills and configured MCP servers
  are themselves machine-wide (`~/.claude/skills/`, `~/.claude.json`).
- **Per-project sections** — one block per project the coordinator has actually
  routed work in, keyed by project path or name, holding what it inferred about that
  project's stack and the workflow patterns that follow from it. Written the first
  time it does real routing work in a project; refreshed when it notices the stack
  has changed (a new dependency, a new framework config file appearing).

When routing inside a given project, the coordinator reads the global section plus
*that project's own* section only — every other project's block is inert history it
skips over, not something re-parsed on every request. This keeps routing overhead
flat regardless of how many projects the registry has accumulated notes on.

## Self-Setup

**Trigger:** the first time `SKILL.md` loads and finds `~/.claude/coordinator-registry.md`
missing or empty, it does not build it unprompted. It says so and offers:

> "I don't have a local registry yet — want me to scan your installed skills and MCP
> servers now?"

A "no" is respected for the rest of that session; the coordinator doesn't re-ask on
every subsequent message. It can still route using only the static `my-superpowers`
registry in the meantime — self-setup makes routing *better*, not a precondition for
routing at all.

**Detection scope for v1** (per the earlier discussion in this design):

- **Skills** — enumerate what's installed under `~/.claude/skills/`, reading each
  one's `SKILL.md` frontmatter (`name` + `description`) the same way Claude Code's own
  skill listing does. No need to open the full body of each skill to register it.
- **MCP servers** — whatever is visible as configured/connected for the current
  session (the same information already surfaced to the coordinator today, e.g. tool
  names prefixed `mcp__<server>__*`, or server names appearing in session context).

Subagent types, hooks, and slash commands are explicitly out of scope for v1 (see Out
of scope).

## Continuous Self-Update

No separate prompt is needed once a registry exists. The core states a standing rule:
whenever the coordinator itself installs a new skill, notices a new MCP server has
connected, or otherwise learns something new about the environment during normal
work, updating the relevant part of `coordinator-registry.md` is part of doing that
work — not a separate maintenance step requiring permission each time. This is local
bookkeeping, not a destructive or user-visible action, so it doesn't need a
confirmation gate the way e.g. discarding a branch does.

The same applies to per-project stack sections: noticing a project's stack changed
(new dependency, new config file) during ordinary routing work is itself the trigger
to refresh that project's section.

## Components touched

| File | Change |
|---|---|
| `skills/coordinator/SKILL.md` | New. The portable core described above. |
| `README.md` | Add a short mention of `coordinator` alongside the existing workflow list, so it's discoverable — it sits above the numbered workflow as a router, not another numbered step. Also add a one-line warning on the install step about the name-collision risk (see Impact analysis). |

Nothing else in the repo changes. This is purely additive at the repo level — no
existing skill's content or behavior is touched *in git*. See the collision risk
below for the one way this stops being true at install time.

## Impact analysis

**Security:** None. No secrets, no network calls beyond what the coordinator already
does when routing to MCP servers a user has separately configured and authorized.

**Blast radius:** None on other skills — this is a new, self-contained skill.
`~/.claude/coordinator-registry.md` is a new file on whatever machine installs this;
it doesn't touch or read any other tool's local state.

**Risk — name collision with an existing personal coordinator:** the README's
documented install step is `cp -r skills/* ~/.claude/skills/`. Shipping this skill as
`skills/coordinator/` means that command will silently overwrite anyone's existing
`~/.claude/skills/coordinator/SKILL.md` — including the author's own, more elaborate
one — with this generic version. "Out of scope" above only holds if the install step
is run selectively rather than as the blanket copy the README currently recommends.
Mitigation for this pass: call this out explicitly in the README's install
instructions (skip or back up an existing `coordinator/` before a blanket copy) rather
than silently trusting users to notice. Actually reconciling an existing personal
coordinator with this one — merging or superseding it — stays out of scope per the
Migration scope decision above; this mitigation only prevents silent data loss, it
doesn't do the merge.

**Compatibility:** None — nothing existing depends on this.

**Data:** `coordinator-registry.md` is plain markdown, human-readable and
human-editable, not a format anything else needs to parse.

## Testing / validation approach

There's no automated test surface for a routing skill's judgment calls (this is true
of the existing `coordinator` and of `using-superpowers` already). Validation is
manual, exercised during implementation:

1. Drop the new `skills/coordinator/` into a clean `~/.claude/skills/` with no
   pre-existing registry, invoke it, confirm it offers to self-setup rather than
   assuming.
2. Accept the offer; confirm it produces a registry with a global skills table and an
   MCP servers table that actually matches what's installed.
3. Route a task inside a project with an identifiable stack (e.g. this repo itself,
   or a sample Expo project if available); confirm a per-project section gets written
   with sensible stack notes and at least one stack-aware workflow pattern.
4. Simulate "installs something new mid-session" (e.g. invoke `find-skills` to add a
   skill) and confirm the global registry section updates without being asked to
   resync.
5. Confirm the static `my-superpowers` skill registry table routes correctly to at
   least a few representative process skills (e.g. a feature request routes through
   `git-branch-workflow` → `brainstorming` → `writing-plans`).
