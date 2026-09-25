# Claude Code and Codex compatibility

**Date:** 2026-09-24

The same my-superpowers skills will support Claude Code and Codex. The user approved
a compatibility migration preserving the existing workflows, then explicitly
limited testing to the changes rather than behavioral testing of the skills.

## Requirements

- Preserve branch tiers, hotfix rules, TDD, human review/approval gates, independent
  agent reviews, fix-loop limits, escalation, and durable artifact formats.
- Keep one canonical skills tree. Host references translate operations; they do
  not replace workflow policy. Direct skill invocation resolves the same mapping.
- Discover actual tool schemas, skill locations, model choices, agent limits, and
  workspace ownership. Missing capabilities are reported; fallback never labels
  self-review as independent review or a shared checkout as isolated.
- Keep local registries separate by host/profile and project scope, outside files
  owned by installation. Live capability availability wins over cached observations.
- Supply a portable installer with a read-only default, explicit destinations,
  conflict detection, ownership/hash tracking, and a bootstrap snippet that can be
  merged into existing instructions. Installing does not edit host configuration.
- Supply Python 3.10+ SDD artifact helpers for PowerShell and Bash; preserve the
  previous Bash entry points and workspace layout. Validate plan identity before
  recovery or cleanup. Preserve existing ledger content.
- Test installer/helper behavior and structural consistency of changed references.
  Do not run behavioral skill evaluations, pressure tests, or fresh-agent scenarios.
- Prepare the repository changes only. Live skill installation is a later step.

## Compatibility boundaries

Python and Git become the common runtime for installation and SDD helpers. The
optional Bash polluter diagnostic and Node/Graphviz renderer keep their explicit
prerequisites. Per-host adapter examples are not promises that every client/version
exposes the same tools. Serial execution remains subject to independent review.

Historical development documents remain records of the earlier Claude-only release.
Existing source checkouts and live installations are never silently overwritten by
the installer. Legacy Claude registry entries may be preserved and validated on
refresh; they cannot establish Codex tool availability.
