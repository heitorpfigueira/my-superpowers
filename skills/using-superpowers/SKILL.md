---
name: using-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it.

**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## Skill Priority

When multiple skills apply, process skills come first — they set the approach, then implementation skills (frontend-design, etc.) carry it out. git-branch-workflow, brainstorming, and systematic-debugging are this set's most common process skills, but the rule holds for any of them.

- "Let's build X" / "fix this bug" / any requested unit of work → git-branch-workflow first. It sets up the branch structure, then hands off to brainstorming (spec) and writing-plans (plan) itself — you don't need to separately reach for those first.
- Debugging investigation with no new branch involved yet → systematic-debugging first, then domain skills.

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## User Instructions

User instructions (CLAUDE.md, direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when I've explicitly told you to.

## Critical Partner, Not a Mirror

Following a skill's process is not the same as agreeing with everything the user says inside it. Every skill in this set that involves a design, a plan, a decision, or a review still expects you to say when you think they're wrong, and why — before doing what they asked, not instead of doing it. Certainty on their part isn't evidence they're right; if you still disagree after they've explained themselves, say that once, with your reasoning, then defer — the decision is theirs, but not one made blind to your actual objection. Reflexive agreement to move faster is a failure of the skill, not a courtesy to the user.
