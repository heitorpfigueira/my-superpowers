---
name: finishing-a-development-branch
description: Use when a parent branch has every child branch merged and passing, or a grandparent branch has every parent branch merged and passing, or a hotfix branch is ready - opens the Pull Request that lands it one tier up (parent to grandparent, grandparent to main, hotfix to main). Not for child branches, which squash-merge inline as part of git-branch-workflow Step 2 and never reach this skill.
---

# Finishing a Development Branch

## Overview

**Core principle:** Verify tests → Detect environment → Determine what this branch lands on → Present options → Execute choice → Clean up.

This skill lands a **parent** or **grandparent** branch (or a **hotfix**, which is parent-shaped but skips the grandparent tier) — see git-branch-workflow for the tier structure. Child branches don't reach this skill at all: they squash-merge into their parent inline, after a human review, as part of Step 2 of that workflow. If a parent branch is finishing, writing-development-report should already have run before this skill starts — its report is part of what the PR shows a reviewer.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## Step 1: Verify Tests

Run the project's full test suite (`npm test` / `cargo test` / `pytest` / `go test ./...`).

**If tests fail**, report the failures and stop — the menu comes after a green suite:

```
Tests failing (<N> failures). Must fix before completing:

[Show failures]
```

**If tests pass:** continue to Step 2.

## Step 2: Detect Environment

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# Capture now, while still inside the workspace — Step 5 changes directory
# before cleanup (Step 6) needs this value
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

This determines how cleanup works (the menu itself, Step 4, is the same 2
options either way):

| State | Cleanup |
|-------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | No worktree to clean up |
| `GIT_DIR != GIT_COMMON`, named branch | Provenance-based (see Step 6) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | Externally managed — leave in place |

## Step 3: Determine Base Branch

The branch name tells you the tier, and the tier tells you the base — no
guessing needed:

Check these shapes **in order** — `_base` is the deciding suffix, so test for it
before the parent pattern, which otherwise also matches a grandparent:

| Current branch shape | Tier | Lands on |
|---|---|---|
| `<release\|patch>-<name>/_base` | Grandparent | `main` |
| `<release\|patch>-<name>/<feature\|bugfix\|documentation>-<topic>` | Parent | `<release\|patch>-<name>/_base` (its grandparent) |
| `hotfix-<topic>` | Hotfix (parent-tier, no grandparent) | `main` |
| `<parent>--<slug>` (contains `--`) | Child | Not this skill — squash-merges into its parent inline, per git-branch-workflow Step 2 |

Worked example: `release-web-calendar/feature-calendar-views` is a parent, so it
lands on `release-web-calendar/_base` — **not** on `main`.

```bash
BRANCH=$(git branch --show-current)
```

If `$BRANCH` doesn't match any of these shapes, this isn't a
git-branch-workflow branch — fall back to asking: "This branch split from
<your best guess> - is that correct?" Either way, confirm the base out loud
before merging: merging into the wrong base is expensive to undo.

## Step 4: Present Options

Parent, grandparent, and hotfix branches always land via Pull Request —
that's the point of the tier structure: every step up gets a reviewable
artifact, not a silent local merge. So the menu is the same 2 options
regardless of worktree state:

```
Implementation complete. What would you like to do?

1. Push and create a Pull Request to <base-branch>
2. Keep the branch as-is (I'll handle it later)

Which option?
```

**Detached HEAD** (externally managed workspace) uses the same 2 options,
just naming the branch explicitly on push (see Step 5).

Present the menu exactly as written — concise, with every option coming
from the list above. Discarding the work happens only in response to your
human partner explicitly asking for it (see "If your human partner asks to
discard the work" below). Wait for their answer; the integration decision
is theirs.

## Step 5: Execute Choice

### Option 1: Push and Create PR

```bash
git push -u origin <feature-branch>
# From a detached HEAD, name the new branch on the remote:
# git push origin HEAD:refs/heads/<new-branch>
```

Then create the pull/merge request against <base-branch> with the forge's
tooling — its CLI if one is available, or the creation URL most forges
print when you push — following the repo's PR template and conventions if
present, and report the URL to your human partner.

The PR's Tests section must cover **both** what you ran and what you couldn't —
see "The Tests Section" below.

Keep the worktree — your human partner iterates on PR feedback there.

### Option 2: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

### If your human partner asks to discard the work

This path exists only as a response to an explicit request to throw the
work away. Confirm first:

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for that exact confirmation. When it arrives:

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

Then clean up the worktree (Step 6) and force-delete the branch:

```bash
git branch -D <feature-branch>
```

## The Tests Section

A reviewer reads "Tests: all passing" as "this was verified." That is only half true
whenever the environment couldn't run part of what matters — a headless container has no
display, no simulator, no `/dev/kvm`. The Tests section therefore has two halves, and
the second is what makes the first honest.

```markdown
## Tests

### Verified here

- `<command>` - <result, with numbers: 151 tests, 5 packages, 0 failures>
- <manual check you actually performed, and how>

### Needs manual verification

Not runnable in this environment: <one line on what blocks it - e.g. built in a
headless Linux container, no display and no simulator, so nothing visual or
native-only can be exercised here>.

**1. <What to check> - <why this change could break it>**

1. <exact command to run>
2. <exact action to take>
3. <exact thing to look at>

**Pass:** <observable criterion>
**Fail:** <the specific wrong behavior to watch for>

**2. <next item, same shape>**
```

Most of this is already written — pull it from the report's "Needs manual verification"
section (writing-development-report) rather than reconstructing it. **Omit the second
half entirely when there's nothing environment-blocked.** An empty or padded section
trains reviewers to skip the heading, including on the PR where it matters.

### What belongs in it

Only checks that are **environment-blocked and relevant to this diff**. The bar is "this
environment physically cannot run it," not "this was tedious to automate" — if it could
be a test, write the test instead. See verification-before-completion for both guards.

### Writing steps a reviewer can actually follow

Assume they have the branch checked out and nothing else. Exact commands, not
descriptions of commands. Name the URL, the screen, the element.

```
BAD:   Check that the drawer animation looks right on mobile.
GOOD:  1. pnpm --filter mobile start --web
       2. Open http://localhost:8081, narrow the window below 768px
       3. Tap the hamburger at top-left
       Pass: drawer slides in from the left over ~300ms, backdrop dims behind it
       Fail: drawer jump-cuts into place, or the backdrop never appears
```

The pass/fail lines are the part that gets skipped and the part that carries the value —
without them you've asked someone to look at a screen without saying what they're
looking for, and any outcome will seem acceptable.

## Step 6: Cleanup Workspace

**Runs only for confirmed discards.** Both Option 1 (Push and Create PR)
and Option 2 (Keep As-Is) preserve the worktree — a pushed branch needs it
for PR feedback, and "keep as-is" means exactly that. Cleanup only happens
when your human partner explicitly asked to discard the work (see above).
That caller has already changed directory to the main repo root — worktree
removal must run from outside the worktree — and uses the
`GIT_DIR`/`GIT_COMMON`/`WORKTREE_PATH` values captured in Step 2, from
before that directory change.

**If `GIT_DIR == GIT_COMMON`:** Normal repo, no worktree to clean up. Done.

**If `WORKTREE_PATH` is under `.worktrees/` or `worktrees/`:** Superpowers
created this worktree — we own cleanup:

```bash
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

**Otherwise:** The host environment owns this workspace — leave it in
place. If your platform provides a workspace-exit tool, use it.

## Quick Reference

| Option | Push | Keep Worktree | Cleanup Branch |
|--------|------|---------------|----------------|
| 1. Create PR | yes | yes | - |
| 2. Keep as-is | - | yes | - |
| Discard (explicit request only) | - | - | yes (force) |

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Tests passed earlier this session" | Run the suite on the tree you are about to integrate. A green run only proves the tree it ran on. |
| "They obviously want it merged" | Integration is your human partner's decision. Present the menu and wait. |
| "They seem done with this feature — I'll offer to discard it" | The menu is complete as written. Discard happens only when your human partner asks for it in so many words. |
| "'Yeah, get rid of it' counts as confirmation" | Only the typed word `discard` authorizes deletion. |
| "The PR is up, so the worktree is clutter now" | PR feedback gets fixed in that worktree. It stays until the work lands. |
| "This other worktree looks stale — I'll clean it too" | Clean up only worktrees under `.worktrees/` or `worktrees/`. Everything else belongs to the host. |
| "I'll just merge this locally, it's faster than a PR" | Parent and grandparent branches land via Pull Request, always — that review artifact is the point of the tier structure, not an optional formality. |
| "The base branch is obviously main" | The branch name shape (Step 3) determines the base — confirm it, don't guess from habit. Merging into the wrong base is expensive to undo. |
| "The push was rejected — force-push will fix it" | A rejected push means the remote moved. Investigate; force-push only on your human partner's explicit request. |
