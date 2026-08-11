---
name: parallel-development
description: Use once git-branch-workflow's spec and plans reveal 2+ independent parent-branch slices that could be built at the same time - spawns one developer agent per slice, each running subagent-driven-development in its own worktree, and routes every human-facing gate back through the core agent.
---

# Parallel Development

## Overview

git-branch-workflow already allows several parent branches under one grandparent
(different slices of one body of work). This skill is what actually builds them
at the same time instead of one after another: one background agent per parent
slice, each a full owner of its own branch, each running today's
subagent-driven-development unchanged inside its own worktree.

**Core principle:** parallelism lives at the *parent* tier, not the task tier.
A developer agent's own task loop stays exactly as sequential as it already is -
nothing about subagent-driven-development changes internally. What's new is that
several of those loops now run concurrently, each isolated in its own worktree,
coordinated by a core agent that never lets an unattended agent make a call that
belongs to the human.

**Announce at start:** "I'm using the parallel-development skill to build these
slices concurrently."

## Naming

- **Core agent** - the agent (interactive session) that took the original
  request, decomposed it into independent slices, and spawns/coordinates the
  developer agents. It is the only party that talks to the human directly.
- **Developer agent** - one named background agent per independent parent
  slice. It owns that parent branch end-to-end: writes or executes its plan,
  dispatches its own implementer/reviewer **subagents** one at a time via
  subagent-driven-development, and closes the branch out.
- **Subagent** stays scoped to what a developer agent (or the core agent
  working solo) dispatches for one task - an implementer or a reviewer. A
  developer agent is never a "subagent" in this skill's vocabulary, even
  though mechanically it is spawned the same way (the `Agent` tool). Keep the
  two words apart in anything you write here or in a dispatch prompt - "don't
  dispatch subagents in parallel" (subagent-driven-development's rule) is
  about a *single* developer agent's own implementers, not about running
  multiple developer agents at once.

## When to Use

```dot
digraph when_to_use {
    "Plan(s) show 2+ independent parent slices?" [shape=diamond];
    "Could they be built at the same time\nwithout touching the same files?" [shape=diamond];
    "Propose parallel dispatch, wait for yes" [shape=box];
    "Work them one at a time (today's git-branch-workflow)" [shape=box];

    "Plan(s) show 2+ independent parent slices?" -> "Work them one at a time (today's git-branch-workflow)" [label="no"];
    "Plan(s) show 2+ independent parent slices?" -> "Could they be built at the same time\nwithout touching the same files?" [label="yes"];
    "Could they be built at the same time\nwithout touching the same files?" -> "Propose parallel dispatch, wait for yes" [label="yes"];
    "Could they be built at the same time\nwithout touching the same files?" -> "Work them one at a time (today's git-branch-workflow)" [label("no - tightly coupled")];
}
```

The independence check is writing-plans' existing Scope Check and File
Structure sections, one level up: each candidate parent slice needs its own
spec and plan already written (brainstorming's sub-project decomposition),
and their File Structure sections should show no file overlap. Overlap
doesn't rule out parallel dispatch - it just means the overlapping area is a
likely scope-bleed candidate (see below), not that the slices must be
serialized.

**Never auto-spawn.** Even when independence looks clean, propose it and wait:

> "These N slices look independent: [list, one line each]. Want me to build
> them in parallel? I'll spawn one developer agent per slice, each in its own
> worktree, and bring every review back to you here."

Spec authoring itself is never parallelized - brainstorming stays one
interactive, sequential conversation with you per sub-project, same as
today. Only *execution* (Step 2 onward of git-branch-workflow) splits across
developer agents, and only after every slice already has an approved spec and
plan.

## Step 1: Set Up Each Developer Agent

The core agent - never the developer agent itself - creates the ground the
developer agent will stand on, so branch naming stays under
git-branch-workflow's convention and the roster (below) always has a real
path to point at:

1. Create the parent branch per git-branch-workflow Step 1 (off the shared
   grandparent).
2. Create a worktree for it per using-git-worktrees, preferring a native
   worktree tool if one is available.
3. Only then dispatch the developer agent, with its worktree path and branch
   name already fixed.

**Dispatch a named background agent per slice** (the `Agent` tool, not a
fork - a developer agent needs its own isolated context, not the core
agent's history). Name it after the parent's topic slug (a parent
`release-calendar-sync/feature-mobile-shell` becomes developer agent
`mobile-shell`) so the roster and any `SendMessage` stay readable.

**Model:** a capable tier, not the cheap tier. A developer agent does
coordination and judgment - running its own subagent-driven-development loop,
adjudicating its own fix-loop rounds - the same job the core agent would do
if it were working this slice directly. Cost savings still happen exactly
where subagent-driven-development already puts them: at the implementer and
reviewer subagents a developer agent dispatches internally.

**Dispatch prompt contents** (self-contained - a developer agent starts with
none of the core agent's context):

- Its worktree path and parent branch name.
- The plan file path (or spec file path, if the plan still needs writing).
- **REQUIRED SUB-SKILL:** use subagent-driven-development to execute it,
  unmodified.
- The relay protocol (next section) in place of every "ask your human
  partner" instruction those skills contain - a developer agent never
  presents a menu or a question to a human directly.
- The scope-bleed protocol (below).
- Its name, and the core agent's name (`main`) to message.

## Step 2: The Relay Protocol

Every gate in git-branch-workflow, subagent-driven-development,
finishing-a-development-branch, local-pull-requests, systematic-debugging,
and test-driven-development that says "ask your human partner" forks on who's
asking:

| Who's asking | What happens |
|---|---|
| The interactive session (core agent working solo, or core agent's own grandparent-level close-out) | Ask directly, exactly as those skills already describe. |
| A developer agent | `SendMessage` to `main` with the gate's content, then stop and wait. Never proceed on its own judgment, never time out into a default. |

This covers, at minimum: git-branch-workflow's child-branch squash-merge
review (Step 2.5) and its local-pull-requests delivery form,
subagent-driven-development's pre-flight conflict scan, its fix-loop
plan-conflict question, its breaker's BLOCKED report,
finishing-a-development-branch's options menu and discard-confirmation,
systematic-debugging's "discuss with your human partner" step after 3+ failed
fixes, and test-driven-development's TDD-exception ask. Anywhere else a
developer agent hits an unlisted "ask the human" instruction, the same fork
applies by default - relay, don't decide.

**The core agent's job while developer agents run** is to sit on this relay:
receive each message, surface it to you exactly as if it had arisen in the
core agent's own execution, wait for your actual answer, then `SendMessage`
the specific developer agent back to unblock it. Multiple developer agents
finishing around the same time just means multiple relayed questions in
sequence - nothing merges, and no menu resolves, without your explicit
answer reaching the developer agent that asked.

## Step 3: Scope-Bleed Handling

A developer agent that notices code outside its task's declared scope - code
that looks like it belongs to (or could break) another slice - does not stop
and does not decide alone:

1. **Flag, don't block.** `SendMessage` `main` naming the file/area, why it
   looks out of scope, and which sibling slice it might affect. Keep working.
2. **Core agent logs it** in the roster (below) as `flagged`, and relays it
   to the named sibling as a non-blocking heads-up.
3. **The sibling self-checks** against its own remaining tasks - cheap, since
   it already holds its own plan - and replies one of two ways:
   - **Not relevant:** one-line reason. The roster entry closes as
     `resolved-not-relevant`. This is still a paper trail, not a discard -
     see below.
   - **Actually relevant:** this is now a real cross-slice conflict the plan
     didn't anticipate. Escalate to Step 4.
4. **Every entry survives**, resolved or escalated. It rolls into that
   developer agent's own writing-development-report (Decisions & Deviations,
   or Follow-ups) and into the parent PR's Impact Analysis (Blast radius) via
   finishing-a-development-branch - the same places subagent-driven-development
   already rolls up deferred minors. A dismissal that turns out wrong three
   tasks later has a record of exactly what was noticed and why it was waved
   off, instead of the collision looking like it came from nowhere.

## Step 4: Real Conflict Resolution

When a scope-bleed flag escalates as actually relevant, or a conflict only
surfaces once both slices are already done, resolve it on a short-lived
**integration branch** - never by having two developer agents edit the same
branch at once. Two agents holding the pen on the same files at the same
time reintroduces exactly the race condition the whole worktree-per-developer-agent
design exists to avoid. Instead: one agent drives, the other is consulted.

| | Caught early (before either parent is done) | Caught late (both parents finished) |
|---|---|---|
| **Where the integration branch forks from** | Whichever parent is further along | The grandparent |
| **What it merges** | The other parent's relevant commits so far | Both finished parents |
| **What detects it** | The scope-bleed self-check (Step 3) | Re-running every already-landed sibling parent's parent-level tests when a new parent merges onto the same grandparent (git-branch-workflow) - a merge can be textually clean and still break a sibling's contract |
| **Who resolves it** | One of the two developer agents, driving | Same pattern - pick the developer agent whose slice is more central to the conflict, or a fresh agent briefed with both sides |
| **The other agent's role** | Consulted via `SendMessage` as the authority on its own code's intent - never a simultaneous co-editor | Same |
| **Where it lands** | Reviewed (Step 2's relay, same human gate as any child branch), then folded back into both parents, which continue independently | Reviewed the same way, then **this branch** - not the second parent's original PR - is what lands on the grandparent |

The review gate here is not optional or lighter than usual because two agents
were involved - if anything, a resolved cross-slice conflict deserves *more*
scrutiny, not less, since it's exactly the kind of change neither slice's
original plan accounted for.

## Step 5: Resilience and Recovery

A developer agent's own compaction resilience is already handled - it runs
subagent-driven-development unmodified, which already tracks progress in a
ledger file and treats git log as more trustworthy than its own memory. That
is inherited for free, not rebuilt here.

What this skill adds is the layer above that: recovering the **core agent's**
picture of which developer agents exist, after the core agent itself is
compacted, restarted, or the session simply ends and resumes later.

**The roster** lives in the core agent's own working directory (the main
checkout, not any spawned worktree) at
`.superpowers/parallel/<grandparent-name>/roster.md`, git-ignored the same
way subagent-driven-development's own workspace is. One entry per developer
agent:

```markdown
## <developer-agent-name>
- Parent branch: <release|patch>-<name>/<kind>-<topic>
- Worktree: <absolute path>
- Plan: <path to its plan file>
- Status: dispatched | awaiting-review | blocked | integration-pending | done
- Last update: <what happened, when>
```

**Recovery never depends on the same agent process surviving.** Every entry
carries enough (parent branch, worktree path, plan file) to redispatch a
*fresh* developer agent pointed at the same worktree and plan if the original
is unreachable - subagent-driven-development's own ledger check
("`Task N: complete` lines are done - resume at the first without one") makes
that redispatch a safe no-op for anything already finished. So recovery is
always the same two-step move regardless of what actually happened to the
agent:

- **Cheap path:** still alive - `SendMessage` it by name, it resumes from its
  own transcript.
- **Fallback path:** gone - spawn fresh, point it at the same worktree and
  plan, let its own ledger tell it where it left off.

git-branch-workflow's existing rule (push the parent to `origin` after every
child squash-merge) is a free offsite backup on top of this - a full local
loss only ever exposes whatever's happened since the last child merged.

## Step 6: Completion

The core agent waits for every developer agent's parent branch to reach
"PR opened" (each developer agent runs finishing-a-development-branch itself
for its own parent, relaying that skill's options menu per Step 2) before
proceeding to the grandparent-level PR. That last step is the core agent's
own - it's the interactive session, so it asks you directly, no relay needed.
This is the same rule git-branch-workflow already states for multiple
parents under one grandparent; parallel-development just means those parents
finished concurrently instead of in sequence.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "The slices look independent, I'll just start them" | Never auto-spawn. Propose it, name the slices, wait for a yes. |
| "This flag is probably nothing, I won't bother logging it" | Every scope-bleed flag survives, resolved or not - it's the paper trail that makes a later collision explainable instead of mysterious. |
| "Both agents can just edit the integration branch together, it'll be faster" | Simultaneous co-editing is the exact race condition worktrees exist to prevent. One drives, one consults. |
| "The developer agent can decide this one, it's a small gate" | Every "ask your human partner" instruction in every skill it runs still means what it says - relay it, don't let a developer agent adjudicate on your behalf. |
| "The original developer agent is gone, so we lost that slice's progress" | Nothing is lost that was committed. Redispatch fresh, pointed at the same worktree - its own ledger tells it exactly where it left off. |
| "This conflict is small, skip the review before landing the integration branch" | A resolved cross-slice conflict is exactly the diff that most needs the human gate, not less of it. |

## Quick Reference

| Situation | Action |
|---|---|
| 2+ independent parent slices identified | Propose parallel dispatch, wait for yes |
| Setting up a developer agent | Core agent creates branch + worktree first, then dispatches, capable-tier model |
| Developer agent hits any "ask human" gate | `SendMessage` `main`, stop, wait to be resumed |
| Developer agent notices out-of-scope code | Flag `main`, keep working, don't block |
| Sibling confirms a flagged overlap is real | Escalate to integration-branch resolution (Step 4) |
| Core agent restarts or compacts | Re-read the roster, resume-by-name or redispatch-fresh |
| All parents' PRs open | Core agent proceeds to the grandparent PR directly |
