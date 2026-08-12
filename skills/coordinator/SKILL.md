---
name: coordinator
description: Routes a task to the right my-superpowers skill, MCP server, or other installed capability before work begins. Consult before non-trivial work — new features, unexplained bugs, multi-step or multi-technology tasks — when more than one skill or server could plausibly apply. Skip for single-file reads, small edits, and status checks. Builds and maintains its own local registry of what's installed rather than shipping one.
argument-hint: "[task description]"
---

# Coordinator

You are acting as the agent coordinator. Your job is to analyze the task and
produce a clear routing plan before any work begins — or, for small requests,
route silently and get on with it. See Step 0.

## Precedence

Once installed and invoked, this file is the authoritative routing source for the
session. Where any other installed skill disagrees about *which* skill or server to
use, this file wins — including skills that open by claiming to be the first thing
to consult (`using-superpowers` and `git-branch-workflow`, if installed, both do
this). They are correct about *how* to do the work once routed; they do not
override this file's triage step. Run triage first, then hand off to them.

**How this file gets invoked** — a slash command, a session-start hook, or simply
being asked for by name — is configured by whoever installed it. This file doesn't
assume a particular trigger mechanism; it only assumes that once it's running, it
routes.

**`my-superpowers` process skills are ordinary Claude Code skills on disk**, invoked
with the `Skill` tool by name — not through an MCP server. If this installation set
them up some other way, the routing table later in this file still applies; only the
invocation mechanism differs.

## Task to Route

$ARGUMENTS

## Step 0 — Triage (always do this first)

Not every request needs a routing plan. Pick a path:

**Fast path — no routing plan.** Do the work directly, loading any obviously
relevant skill as you go:
- Reading or searching code; answering questions about existing code
- One-line or single-function edits, renames, small fixes
- Status checks, git queries, file listings, config lookups
- Follow-ups continuing work already routed earlier in this session
- Anything where exactly one tool or skill obviously applies

**Full path — produce the Routing Plan below.** Use it when:
- Building a new feature, component, or system
- Debugging something whose cause is not already known
- Multi-step work spanning several files or technologies
- Two or more skills or servers could plausibly apply and the choice matters
- The task uses a library whose current API should be verified before writing code

When in doubt, prefer the fast path. A routing plan on a trivial request wastes
the user's time; skipping one on genuinely complex work costs more.

**Route each task once.** Never re-present a routing plan for work already routed
in this session.

### Full path

1. Using the registries available to you — the static one later in this file, plus
   `~/.claude/coordinator-registry.md` if it exists (see Self-Setup) — produce a
   **Routing Plan** in this exact format:

---

### Routing Plan

**Task summary:** _(one sentence)_

**Process skill(s) to invoke first:**
- `skill-name` — reason

**MCP server(s) or other installed capability to use:**
- `server-or-skill-name` — what for

**Execution skill(s) to apply:**
- `skill-name` — when/why

**Suggested workflow sequence:**
1. Step one
2. Step two
3. ...

**Caveats / blockers:**
- _(e.g. missing credentials, a required local service not running)_

---

2. After presenting the plan, ask: **"Shall I proceed with this plan?"**

3. If the user confirms, **before writing any code**, load every library or
   framework skill that applies to the technologies involved. Load them all first,
   then begin implementation. Never skip this step — stale knowledge causes wrong
   patterns.

If `$ARGUMENTS` is empty, review the current conversation to infer the task, then
produce the routing plan for it.

## my-superpowers Process Skill Registry

Invoke with the **`Skill` tool**, by the exact name shown. Source of truth for the
skill content itself is the `my-superpowers` repo this coordinator shipped with —
this table only needs updating here if a future version of that repo adds, removes,
or renames a skill.

These skills assume each other: `git-branch-workflow` is the entry point and drives
the spec → plan → implement → report sequence, calling the others at the right
moments. Routing to one of the later skills without having opened a branch structure
usually means the triage was wrong.

`parallel-development`, if installed, introduces two roles: the *core agent* (the
session that took the request and orchestrates) and *developer agents* (one per
parallel parent-branch slice). Don't confuse either with a *subagent* — that word
stays scoped to the implementer/reviewer agents `subagent-driven-development`
dispatches for one task at a time.

### Process Skills — invoke FIRST, they define HOW to approach the task

| Skill | When to invoke |
|---|---|
| `git-branch-workflow` | **The entry point for any requested unit of work** — before brainstorming, before touching code. Establishes the three-tier grandparent/parent/child structure, drives spec → plan → implement → report, defines the commit message format, and covers hotfixes (which skip the grandparent tier) |
| `brainstorming` | Before ANY feature, component, or creative work — even if requirements seem clear. Produces a spec in `docs/development/spec/` |
| `writing-plans` | When you have an approved spec or multi-step requirements, before touching code. Produces a plan in `docs/development/plan/` |
| `systematic-debugging` | Any bug, test failure, or behavior that doesn't match expectations |
| `verification-before-completion` | Before claiming work is done, fixed, or passing — evidence before assertions |

### Execution Skills — invoke AFTER the relevant process skill

| Skill | When to invoke |
|---|---|
| `test-driven-development` | Before writing any implementation code — write the test first |
| `subagent-driven-development` | Running a plan's tasks in the current session, one child branch at a time, with review checkpoints |
| `executing-plans` | Running a written plan with review checkpoints in a fresh session (use when you don't have subagent access) |
| `dispatching-parallel-agents` | 2+ fully independent tasks with no shared state, dispatched to separate agents |
| `parallel-development` | `writing-plans` or `brainstorming` has identified 2+ independent parent-branch slices (no file overlap) that could be built at the same time. Spawns one developer agent per slice, each running `subagent-driven-development` in its own worktree; always asks before spawning anything |

### Integration Skills

| Skill | When to invoke |
|---|---|
| `requesting-code-review` | After completing a task or feature, before a child branch squash-merges into its parent |
| `local-pull-requests` | **Optional.** Opens a real PR on a self-hosted Forgejo/Gitea for a child branch. Use at git-branch-workflow's Step 2.5 gate whenever a local forge is configured — run its own detection step rather than assuming; without one, that gate delivers the same description in chat instead |
| `receiving-code-review` | Before implementing review feedback — don't blindly apply suggestions, including your human partner's own |
| `writing-development-report` | Once every child branch under a parent is merged and green — the closing summary, saved to `docs/development/report/`. Also when the user asks "what did we just build" for completed work |
| `finishing-a-development-branch` | Opens the PR that lands a branch one tier up (parent → grandparent, grandparent → main, hotfix → main). **Not** for child branches, which squash-merge inline |
| `writing-documentation` | Whenever project knowledge needs a durable home — architecture decisions, technology choices, business rules, a new coding convention. The living docs in `docs/`, as opposed to the point-in-time spec/plan/report set |
| `using-git-worktrees` | Before feature work that needs filesystem isolation from the current workspace |

### Meta Skills

| Skill | When to invoke |
|---|---|
| `using-superpowers` | Establishes the skill-discovery protocol, if installed. Subordinate to this file's triage — see Precedence |
| `writing-skills` | Creating or editing any skill in the `my-superpowers` set, including this one |

## Common Workflow Patterns

Stack-agnostic patterns only — anything stack-specific belongs in a project's own
registry section (see Stack Adaptation), not here.

| Goal | Skill sequence |
|---|---|
| Build a new feature | `git-branch-workflow` → load relevant library skills → `brainstorming` → `writing-plans` → `subagent-driven-development` (per child branch: `test-driven-development` → `requesting-code-review`) → `writing-development-report` → `finishing-a-development-branch` |
| Fix a bug | `git-branch-workflow` → `systematic-debugging` → fix → `verification-before-completion` |
| Ship an urgent hotfix | `git-branch-workflow` (hotfix path — skips the grandparent tier) → fix → `verification-before-completion` → `writing-development-report` → `finishing-a-development-branch` |
| Complete and ship a branch | `verification-before-completion` → `requesting-code-review` → `writing-development-report` → `finishing-a-development-branch` |
| Capture a decision or convention | `writing-documentation` (living docs in `docs/`, not the spec/plan/report set) |

## Routing Decision

```dot
digraph coordinator {
    rankdir=TB;
    "Task received" [shape=doublecircle];
    "Creative or feature work?" [shape=diamond];
    "Bug or unexpected behavior?" [shape=diamond];
    "Multi-step task with requirements?" [shape=diamond];
    "brainstorming" [shape=box];
    "systematic-debugging" [shape=box];
    "writing-plans" [shape=box];
    "Need a capability beyond process skills?" [shape=diamond];
    "Consult local registry for the right server/skill" [shape=box];
    "Execute (TDD + verify)" [shape=doublecircle];

    "Task received" -> "Creative or feature work?";
    "Creative or feature work?" -> "brainstorming" [label="yes"];
    "Creative or feature work?" -> "Bug or unexpected behavior?" [label="no"];
    "Bug or unexpected behavior?" -> "systematic-debugging" [label="yes"];
    "Bug or unexpected behavior?" -> "Multi-step task with requirements?" [label="no"];
    "Multi-step task with requirements?" -> "writing-plans" [label="yes"];
    "Multi-step task with requirements?" -> "Need a capability beyond process skills?" [label="no"];

    "brainstorming" -> "Need a capability beyond process skills?";
    "systematic-debugging" -> "Need a capability beyond process skills?";
    "writing-plans" -> "Need a capability beyond process skills?";

    "Need a capability beyond process skills?" -> "Consult local registry for the right server/skill" [label="yes"];
    "Need a capability beyond process skills?" -> "Execute (TDD + verify)" [label="no"];
    "Consult local registry for the right server/skill" -> "Execute (TDD + verify)";
}
```

## Self-Setup

`my-superpowers`'s own process skills are fixed at authoring time (the registry
above). Everything else — what other skills are installed, what MCP servers are
configured, what stack a given project uses — is specific to the machine and
project this coordinator is running in, and gets recorded in
`~/.claude/coordinator-registry.md` instead of in this file.

**Why a separate file, and why that exact path:** this file (`SKILL.md`) is
versioned — updating `my-superpowers` (pulling a new version of the repo,
re-copying the skill directory) replaces it wholesale. A generated registry has to
live somewhere that update can never touch, so it lives outside the
`skills/coordinator/` directory entirely, at a fixed path directly under
`~/.claude/`. That way a `my-superpowers` update, a straight re-copy of this skill,
or even a full reinstall never wipes out what a machine has already learned about
itself.

**Registry format:**

~~~markdown
# Coordinator Registry

_Generated and maintained by the coordinator skill. Safe to read; sections may be
rewritten the next time the coordinator refreshes them._

## Installed Skills

| Skill | Description |
|---|---|
| <name> | <description, from that skill's own SKILL.md frontmatter> |

## MCP Servers

| Server | Notes |
|---|---|
| <name> | <what it's for> |

## Projects

### <project path or name>

**Stack:** <inferred stack summary>

**Workflow patterns:**
- <pattern learned for this project>
~~~

**Trigger:** the first time this file loads and `~/.claude/coordinator-registry.md`
is missing or empty, don't build it unprompted. Say so and offer:

> "I don't have a local registry yet — want me to scan your installed skills and MCP
> servers now?"

A "no" is respected for the rest of that session — don't re-offer on every
subsequent message. Routing still works without it, using only the static registry
above; self-setup makes routing *better*, not a precondition for routing at all.

**What "scan" means, for v1:**
- **Skills** — enumerate what's installed under `~/.claude/skills/` (or wherever this
  installation's skills live) and read each one's `SKILL.md` frontmatter (`name` +
  `description`). That's enough to register it — no need to read the full body.
- **MCP servers** — whatever is visible as configured or connected for the current
  session (tool names prefixed `mcp__<server>__*`, or server names surfaced in
  session context).

How exactly to enumerate skills or recognize an MCP server's purpose from what's
visible is a judgment call, not a fixed procedure — use your own understanding of
what's in front of you, the same way you'd read any other unfamiliar directory or
tool list. Detecting anything beyond skills and MCP servers (subagent types, hooks,
slash commands) is out of scope for now; extend the same way if it's ever needed.

## Continuous Self-Update

Once a registry exists, no separate prompt is needed to keep it current. Installing
a new skill, noticing a new MCP server connect, or otherwise learning something new
about the environment during ordinary work is itself the trigger to update the
relevant part of `~/.claude/coordinator-registry.md` — immediately, as part of doing
that work, not as a separate maintenance step requiring permission each time. This is
local bookkeeping, not a destructive or user-visible action, so it doesn't need a
confirmation gate the way discarding work or pushing to a remote would.

## Stack Adaptation

Nothing in this file names a specific library, framework, or MCP server — that's
deliberate, so it stays true for an arbitrary Claude Code install. But a specific
project you're routing inside of does have a stack, and generic routing alone
under-serves it.

When you do real routing work inside a project for the first time, notice what
you can about its stack — dependency manifests, config files, the code already
there — and write a section for it under `## Projects` in the registry, including
workflow patterns that follow from that stack (the same shape as the generic
patterns above, just specific to what this project actually uses). Refresh that
project's section when the stack changes — a new dependency, a new framework config
file appearing — the same way installing a new skill triggers a registry update
above.

When routing inside a project, read the global sections of the registry plus *that
project's own* section only. Every other project's section is inert history — skip
over it rather than re-parsing it on every request. This keeps routing overhead flat
no matter how many projects the registry has accumulated notes on.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "No registry exists, I'll just build one silently" | Offer first, on the first load only. A silent build is exactly the "assume rather than ask" failure the bootstrap trigger exists to prevent. |
| "They said no to self-setup once, I'll offer again next message" | Respected for the rest of that session. Routing still works from the static registry alone — repeatedly re-offering is friction, not helpfulness. |
| "I just installed a skill, I'll update the registry the next time it matters" | The trigger is "installed, discovered, or learned" — immediately, not deferred. A stale registry is a routing mistake waiting to happen. |
| "This project's stack is obvious, no need to write it down" | Obvious to you this session isn't obvious to the next session, or to the static registry alone. Write the section. |
| "I'll bake a stack-specific rule into this file since I use it on every project" | This file ships to other machines and other stacks. Stack-specific content belongs in the generated registry's per-project section, never here. |
| "The other projects' sections might be useful context, I'll read them too" | They're inert history for routing purposes. Reading them on every request is exactly the unbounded-growth cost this design exists to avoid. |
