---
name: writing-development-report
description: Use when every child branch under a parent branch is merged and its tests pass, right before opening the Pull Request to the grandparent branch - writes the closing summary of everything built and every decision made while working the parent branch. Use when the user asks for a summary, writeup, or report of finished work, or asks "what did we just build" / "what changed" for a completed parent branch.
---

# Writing a Development Report

## Overview

The spec said what to build and why. The plan said how. Neither says what actually happened — where the plan was followed exactly, where reality forced a different call, and what the net result was. The report is that record, written once, at the close of a parent branch, from the vantage point of everything now being done.

**Announce at start:** "I'm using the writing-development-report skill to write up what was built on this branch."

**Save to:** `docs/development/report/YYYY-MM-DD-<topic>-report.md`, committed to the parent branch as part of closing it out.

## Gathering the Material

Before writing, reconstruct what actually happened rather than relying on memory of it:

- `git log --oneline <grandparent>..<parent>` — the sequence of squash-merged child branches tells you the actual shape the work took.
- The spec (`docs/development/spec/...`) and plan (`docs/development/plan/...`) for this topic — what was intended.
- Any parked or deferred findings from code review during the child-branch work.
- Any checks flagged along the way as unrunnable in this environment (git-branch-workflow
  Step 2.2). Collect them now while the reasons are still reconstructable — by PR time,
  "the drawer animation was never actually seen by anyone" is much harder to recover.
- Anything written to `docs/` via writing-documentation during this parent branch's work — new conventions, architecture notes, glossary terms.

## Report Structure

```markdown
# <Topic> - Development Report

**Parent branch:** <release|patch>-<name>/<feature|bugfix|documentation>-<topic>
**Spec:** docs/development/spec/<file>
**Plan:** docs/development/plan/<file>
**Date:** YYYY-MM-DD

## Summary

<A few sentences: what this parent branch set out to do, and
whether it landed as planned. This is the paragraph someone reads
if they read nothing else.>

## What Was Built

<Per child branch (or grouped where several were small and related):
the functionality slice, and the behavior it adds or changes -
same behavior-and-intent framing as the commit messages that built
it, not a list of touched files.>

## Decisions & Deviations

<Anywhere the implementation diverged from the plan, and why - a
child branch that needed splitting, an approach the plan assumed
that didn't hold up, a scope cut. Include decisions that came up
mid-implementation and weren't in the spec at all. If there were
none, say so explicitly rather than omitting the section - an
absent section reads as "nobody checked," a one-line "followed the
plan as written" reads as verified.>

## Testing

<What test coverage this parent branch ends with - the parent-level
tests from Step 1, plus what each child branch added. Confirm
everything is green as of this report, not as of some earlier point
in the work.>

### Needs manual verification

<Checks that matter for this work but that this environment cannot
run - see verification-before-completion. Omit the section entirely
if there are none; do not pad it. For each item: what to check, why
this change could break it, numbered steps, and explicit pass/fail
criteria. Same content carries into the PR body.>

## Documentation Updates

<Any docs/ entries created or updated during this work (link them) -
new glossary terms, architecture notes, coding conventions. If none,
say so.>

## Follow-ups

<Anything explicitly deferred rather than done - a parked code
review finding, a scope cut that should become its own future grandparent,
a TODO that's real and not a placeholder. Not a wishlist - only things
someone actually decided to defer.>
```

## Before Committing It

Read it back against the spec: does every requirement in the spec show up somewhere in "What Was Built," either as done or as an explicit, explained deviation? A report that silently drops a spec requirement is worse than one that flags it as cut.

Commit the report to the parent branch, then hand off to finishing-a-development-branch to open the PR to the grandparent.
