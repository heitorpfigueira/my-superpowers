---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## When Verification Is Impossible In This Environment

The Iron Law has two outcomes: verified, or don't claim it. There is a third state it
doesn't cover — a check that genuinely matters but that **no amount of effort in this
environment can run**. A headless container has no display, no simulator, no
`/dev/kvm`; a machine with no card reader can't test the card reader.

Staying silent about these is its own failure. The claim "tests pass" is true and also
misleading if a reviewer reads it as "this was verified." The rule is:

```
CANNOT VERIFY HERE  ->  RECORD IT AND HAND IT OFF
                        (never silently, never as if verified)
```

Record: what to check, why this change could break it, the exact steps to run it, and
what pass and fail look like. That turns a gap into a task someone can actually pick up.
These items flow into the report (writing-development-report) and then into the PR body
(finishing-a-development-branch), where the reviewer sees them.

**Two guards, or this section becomes a dumping ground:**

1. **Environment-blocked, not effort-blocked.** The bar is "this environment physically
   cannot run it," not "this would take a while" or "this is awkward to automate." If it
   could be a test, write the test. Offloading automatable work onto a human reviewer
   under this heading is a way of skipping it.
2. **Scoped to this change.** List only what this diff could plausibly break. A standing
   list of everything the environment can't do belongs in the project's docs once, not
   re-pasted into every PR — a reviewer who sees the same block every time stops reading
   it, including the time it matters.

| Situation | Handling |
|---|---|
| Headless env, change alters animation/layout/theme | Record it — a human with a display must look |
| No simulator, change touches native-only navigation | Record it — needs a real device or simulator |
| Change is logic-only, rendering untouched | Don't record it — nothing visual is at risk |
| "Writing this test is tedious" | Not this category. Write the test. |
| "The whole app should be smoke-tested" | Too broad to action. Scope it to what changed. |

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness
