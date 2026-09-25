# Host compatibility contract

This reference translates operations for Claude Code and Codex. The workflow's
branch tiers, TDD, independent reviews, fix limits, human gates, and durable
artifacts remain defined by the existing skills. Read this once per session before
tool operations, including direct invocation of an individual skill. This is not
a request to restart skill discovery or route a task again.

## Instructions and routing

Host system/developer instructions and permissions remain authoritative. Explicit
user instructions, including an opt-out from skills, override this package's
defaults. Applicable project instructions (CLAUDE.md or AGENTS.md) customize the
workflow within those boundaries. A skill cannot grant a tool permission.

For an unrouted request: coordinator triage first (if installed), then
using-superpowers discovery, then the chosen process/execution skills. Fast-path
reads and status checks do not open branches or require a routing approval.
For work already routed, continue it. A dispatched worker follows its brief and
loads only the referenced skills; it does not bootstrap the entire workflow.

Select [Claude Code](claude-code.md) or [Codex](codex.md) from the actual session,
not from which folders happen to exist. Both clients can be installed together.
Use [shells.md](shells.md) for shell translation and portable helpers.

## Resolve capabilities from this session

Use the host's exposed tool schemas and installed skill catalog. Record these
bindings in working context; do not assume a tool exists because a cache names it.

| Operation | Required binding |
|---|---|
| Load skill | Exact installed SKILL.md path and native skill loader, if exposed |
| Run command | Available shell/exec tool, shell dialect, explicit working directory |
| Dispatch worker | Available spawn tool, required fields, agent capacity and nesting limits |
| Fresh context | Tool's isolated-context setting; no inherited conversation history |
| Message/resume worker | Live-message or follow-up/resume tool and returned worker identity |
| Await result | Host wait/result mechanism; distinguish idle, running, and completed |
| Ask human | Host question mechanism or normal chat; actual answer required at a gate |
| Track tasks | Native progress tool if exposed, otherwise markdown checklist plus SDD ledger |
| Create worktree | Current workspace owner's tool if available, otherwise git worktree |
| Choose model | Available, permitted model choices and per-dispatch support |

Prompt templates describe a worker request, not a literal tool-call schema.
Translate their fields to the current dispatch tool. Every dispatch supplies a
role, worktree path, controller identity, required artifacts, and relevant
constraints. Store the returned worker identity for subsequent messages.
`CONTROLLER_ID` means that supplied identity; it is never a hardcoded `main` or
`/root`. Worktrees and contexts are separate: a fresh context does not imply an
isolated filesystem. Set the working directory explicitly for each worker call.

## Preserve gates when a capability is missing

- No worker dispatch: offer the existing executing-plans path when appropriate.
  A separate independent review remains required wherever the workflow calls for
  it. Prepare its package and report the unavailable reviewer as a blocker; a
  controller's self-review is not an independent review.
- No live messaging: use a supported resume/follow-up call, or a fresh worker with
  its brief, report, ledger, and outstanding question. A worker waiting at a human
  gate stays waiting until the controller relays the human's actual answer.
- No nested delegation or insufficient slots: execute parent slices sequentially
  from the controller, using separate implementer/reviewer calls. If even that
  cannot supply independent review, stop at that requirement. Do not fill every
  slot with developers who all need another worker to make progress.
- No isolated worktree: do not run parallel writers in a shared checkout. Use the
  host's normal permission mechanism or serialize the slices, retaining all gates.
- Model selection unavailable: use a host-assigned model only if it meets the
  role's required capability. Record that selection is host-controlled. If the
  required escalation/final-review capability cannot be supplied, report the
  limitation; do not invent a model name or bypass the host's restrictions.

Availability alone does not authorize delegation. Follow the user's instruction,
the applicable workflow's delegation rules, and the host's policy. Existing human
gates still apply; elapsed time, an idle worker, and a green test are not approvals.

## Local state

Resolve the state directory in this order: explicit installation/activation
instruction; `MY_SUPERPOWERS_STATE_DIR` if set; the host default in its reference.
`COORDINATOR_REGISTRY` is `<state directory>/coordinator-registry.md`. This is a
resolved path in prose, not shell syntax to copy unchanged into commands.

State lives outside installed skill folders. Keep Claude and Codex state separate,
and use a separate state directory when a profile has a different capability set.
Registry entries record host/profile, project scope, source path, and when observed.
Project-only tools stay in that project's section. Cached entries are hints, never
proof that a capability is currently callable. Reconcile removed/renamed skills
against the current catalog instead of continuing to route to stale entries.
Record capability metadata only, never credentials or raw configuration contents.
If state is unwritable, route from the live catalog and static registry; report
that caching is unavailable without pretending a file was written.

Claude's older `~/.claude/coordinator-registry.md` may be read as a legacy cache
only for that same Claude installation. Preserve it; migrate validated entries
during the next authorized registry refresh. Never import it as Codex availability.
