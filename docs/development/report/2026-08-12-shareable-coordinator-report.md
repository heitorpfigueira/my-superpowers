# Shareable Coordinator - Development Report

**Branch:** custom-workflow-improvement (worked directly on it — see Decisions & Deviations)
**Spec:** docs/development/spec/2026-08-12-shareable-coordinator-spec.md
**Plan:** docs/development/plan/2026-08-12-shareable-coordinator-plan.md
**Date:** 2026-08-12

## Summary

This branch adds a `coordinator` skill to the `my-superpowers` repo: a portable
routing skill that anyone can drop into `~/.claude/skills/` alongside the rest of
the set. Its static content — role, precedence, triage logic, and the
`my-superpowers` process-skill registry — ships fixed and versioned; everything
machine-specific (other installed skills, MCP servers, per-project stack notes) is
detected and recorded by the coordinator itself at `~/.claude/coordinator-registry.md`,
a file deliberately kept outside the skill folder so a repo update can never wipe out
what a given machine has already learned about itself. It landed as planned: all six
plan tasks shipped verbatim content with no unresolved deviations, and the one
substantive gap the final review found — the routing digraph's missing Fast-path
branch — was fixed and re-verified before this report was written.

## What Was Built

**Task 1 — Scaffold** (`d068ea3`): the skill's entry point — frontmatter, a
`Precedence` section establishing this file as the session's authoritative routing
source, and `Step 0 — Triage`, which decides whether a request needs a full Routing
Plan or can be handled silently (fast path).

**Task 2 — Static registry, patterns, digraph** (`72bf40b`): the fixed knowledge
that's accurate for any machine running this version of `my-superpowers` — the
process/execution/integration/meta skill tables, a set of stack-agnostic workflow
patterns ("build a feature," "fix a bug," etc.), and a `Routing Decision` digraph
visualizing the same logic.

**Task 3 — Self-Setup** (`8e4eba0`): defines `~/.claude/coordinator-registry.md`'s
format (Installed Skills table, MCP Servers table, per-project sections) and the
bootstrap trigger — offer to scan on first use rather than assuming or silently
building one. Verified with a RED (offer absent) / GREEN (offer present) micro-test
pair, since this behavior was genuinely uncertain going in.

**Task 4 — Continuous Self-Update + Stack Adaptation** (`9de94fd`, `8cca3f9`, two
commits for two concerns): installing a skill or discovering an MCP server updates
the registry immediately, not on request; and the coordinator notices a project's
stack on first real routing work there and records stack-aware patterns in a
per-project registry section, reading only that project's own section on later
visits rather than every project it's ever touched.

**Task 5 — Common Rationalizations** (`cc4c10f`): the closing table every
`my-superpowers` skill carries, addressing the specific shortcuts the new
self-setup/self-update/stack-adaptation behaviors make possible.

**Task 6 — README** (`6d128a3`): a discoverability mention above the numbered
workflow list, plus a warning that the README's own `cp -r skills/* ~/.claude/skills/`
install step will silently overwrite an existing personal `coordinator` skill —
a real risk this spec's own self-review caught before it shipped as a silent trap.

## Decisions & Deviations

**No tiered branch structure.** This work was explicitly directed to skip
git-branch-workflow's grandparent/parent/child tiers and land directly on
`custom-workflow-improvement` — a standing decision for this repo's own meta-work
made earlier in the session, reconfirmed for this plan's pre-flight conflict scan.
Task reviews and the final whole-branch review still ran in full; only the branch
tiering and per-task child branches were skipped, since the plan's tasks were
strictly sequential edits to one file with no parallelism to protect.

**Micro-tests substitute for automated tests.** This repo has no test runner — it's
skill content, not application code. Each task's plan brief specified a micro-test
(one fresh subagent rep, or a RED/GREEN pair for Task 3's genuinely uncertain
behavior) as this project's equivalent of watching a test fail then pass. This was
a plan-level decision, not an implementation shortcut — documented in the plan's
Global Constraints and confirmed sound by every task reviewer.

**One residual finding from the final review, fixed directly rather than via a
second automated fix wave.** The final whole-branch review found 2 Important + 7
Minor issues; a single fix-wave subagent addressed all of them plus ran the one
real end-to-end test the design had never actually executed (see Testing). The
scoped re-review that followed found 9 of 10 findings fully addressed and one
partially addressed: the Routing Decision digraph's fix added `git-branch-workflow`
and chained `brainstorming → writing-plans` correctly, but still had no branch
representing Step 0's Fast-path behavior, and its new confirm-gate node now applied
to every path — including trivial ones — contradicting Step 0's own prose.
Per subagent-driven-development's "no second fix wave" rule, this surfaced as a
decision rather than triggering another automated round; the fix (`ccd492b`) was
made directly at that point, adding a `Fast-path eligible?` branch that bypasses
`git-branch-workflow` and the confirm gate entirely, matching Step 0 exactly.

**Migrating the author's own personal `~/.claude/skills/coordinator` is explicitly
out of scope**, per the spec — that file keeps working exactly as it does today.

## Testing

No automated test suite exists for this repo (skill/prompt content, not code).
Verification was:

- One micro-test per task (a fresh subagent dispatched with the draft file as
  system context and a realistic user message), except Task 3's RED+GREEN pair and
  Task 5/6's self-review read-backs, which had no behavior to exercise.
- A final whole-branch review (Opus) checking cross-section consistency the
  per-task reviews couldn't see — this is what caught the digraph gap.
- A **real end-to-end test**, run once during the final fix wave: a genuine fake
  `~/.claude/skills/`-equivalent directory with three fake sibling skills was built
  under the plan's (now-deleted) workspace, a fresh subagent with real Bash/Read/
  Write/Glob tools was given the finished `Self-Setup` section and asked to scan and
  build a registry, and it did — producing a correctly-formatted
  `coordinator-registry.md` that accurately listed the three fake skills and
  correctly excluded `coordinator` itself. This was the one thing no prior
  simulated micro-test had actually exercised (writing a real file from a real
  directory scan), and it passed.
- A scoped re-review confirming the fix wave and verifying the e2e registry file's
  content directly rather than trusting the fix report's description of it.

### Needs manual verification

None outstanding. Everything flagged by the final review either had a real
automated-agent check run against it (the e2e test) or was a prose/content fix
verified by direct reading (the digraph, the registry-scope clause, and the seven
minor wording fixes) — nothing in this branch depends on a display, simulator, or
other environment this container lacks.

## Documentation Updates

None. No new architectural decision, technology choice, or convention emerged
during this work that needed a `docs/` entry via writing-documentation — the spec
and this report are this unit of work's own record.

## Follow-ups

- **Registry Hygiene note (v2 candidate).** The final review's Recommendation #4:
  the exclusion clause added in the fix wave (Self-Setup's scan skips skills already
  in the static registry) sidesteps the static/generated dual-source-of-truth risk
  for now, but doesn't cover what happens if the two genuinely disagree after a
  `my-superpowers` update (a renamed or removed skill). Not designed or scoped here.
- **Digraph/table consistency as a standing review check.** The final review's
  Recommendation #2: when a future task appends both a table and a diagram of the
  same routing logic, a task-scoped micro-test can verify the table without ever
  checking the diagram agrees with it — as happened here. Worth a line in future
  task briefs that touch both, not acted on generally in this branch.
- **Migrating the author's personal coordinator** onto this design remains a
  separate, later task, per the spec's explicit scope decision.
