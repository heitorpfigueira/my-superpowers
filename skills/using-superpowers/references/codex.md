# Codex mapping

- Read the chosen SKILL.md using the catalog's exact path. Do not call a Claude
  `Skill` tool or assume slash-command arguments are injected into the file.
- The documented personal location is `~/.agents/skills`; repositories can use
  `.agents/skills`. Managed clients may supply other roots. Prefer their live
  catalog and an explicit installer destination when needed.
- For automatic activation, merge the bootstrap block into the active AGENTS.md.
  Global guidance lives under `CODEX_HOME` (default `~/.codex`); an existing
  AGENTS.override.md can take precedence. Preserve existing content. Explicit
  skill invocation works without a bootstrap block.
- Map delegation to the exposed spawn, message/follow-up, and wait tools. For
  example, some sessions expose `collaboration.spawn_agent`, `send_message`,
  `followup_task`, and `wait_agent`; others use different names. Inspect schemas.
- Request a fresh context when supported (for example `fork_turns="none"`). Pass
  the worktree path explicitly: spawned agents can share the parent's filesystem
  and starting directory. Never assume dispatch creates a worktree.
- Only set model/effort fields when supported and permitted. Honor available
  capacity and depth limits; use the contract's fallback when nesting is unavailable.
- Default state: `<CODEX_HOME or ~/.codex>/my-superpowers`.

References checked 2026-09-24:
[skills](https://learn.chatgpt.com/docs/build-skills),
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
