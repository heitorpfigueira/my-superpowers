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
