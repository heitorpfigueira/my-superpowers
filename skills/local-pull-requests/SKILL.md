---
name: local-pull-requests
description: Use to run git-branch-workflow's child-branch review gate as a real Pull Request instead of a chat message, whenever a local forge is configured for the project - the default way to review a child branch, not a special case reserved for code that must not reach a public remote (that's just one reason a project might set one up). Opens a GitHub-style PR on a self-hosted Forgejo/Gitea running locally. Optional - if the project has no local forge, git-branch-workflow's review gate falls back to delivering the same description in chat.
---

# Local Pull Requests

## Overview

git-branch-workflow's child branches never reach `origin` — they squash-merge into
their parent and disappear. But its Step 2 review gate is a **hard gate**, and a
one-line "please review" in chat is a poor way to review a real diff. A local forge
closes that gap: a GitHub-style PR, with a file-by-file diff and inline comments, for
every child branch, sensitive or not.

**Not just for code that can't leave the machine.** That property (a local forge
never sends the diff to a public remote) makes this the right call for genuinely
sensitive code, but it's one reason to set a forge up, not the qualifying condition
for using this skill once one exists. If a local forge is configured for the project,
it's the default way to run the child-branch review gate, full stop — an ordinary
feature branch gets the same better review experience a security-sensitive one would.

**This skill is optional in the sense that no forge is required.** It describes one
way to run the review gate, not a requirement of the workflow. If the project has no
local forge configured, the gate still happens — git-branch-workflow just delivers
the same change description in chat and waits for approval there. **The description
is identical either way**; only the delivery differs. But "optional" is about whether
a forge exists, not about whether to use one that does — see Detecting a Configured
Forge below.

**Announce at start:** "I'm using the local-pull-requests skill to open this branch for
local review."

## Detecting a Configured Forge

Every time git-branch-workflow's review gate fires, check for a forge — don't default to
chat delivery without checking, and don't rely on remembering from earlier in a longer
session if that memory might be stale:

1. **A `review` remote already exists** (`git remote get-url review` succeeds) — this
   repo was set up for local review before. Reuse it; skip straight to Environment below.
2. **A forge address is declared** elsewhere you'd already know it — the project's own
   instructions (CLAUDE.md, a project-level skill), or something your human partner told
   you earlier this session (an `FJ`/`FORGEJO_URL` value, "the forge is at
   `http://localhost:3000`"). Use it.
3. **Neither exists:** ask once — "Do you have a local Forgejo/Gitea instance for this
   project? If so, what's its address?" Remember the answer for the rest of the session:
   a "no" means chat delivery for every remaining review gate this session, not just this
   one; a "yes" means don't ask again either, just reuse the address.
4. **Before trusting any address found this way, run the preflight below.** A stale or
   wrong address is worse than no address — it produces a hang or a confusing error
   instead of a clean fallback to chat.

This turns git-branch-workflow's "if the project has a local forge configured" into a
real, repeatable check instead of an assumption made once (or never made at all) and
carried forward regardless of whether it's still true.

## Hard rules

1. **Never push to `origin`.** `origin` is the public remote. The entire point is that
   this code does not go there. Push only to the review remote. If a command you are
   about to run contains `push origin`, stop.

   **This rule is scoped to child branches only.** It does not extend to parent or
   grandparent branches — those push to `origin` and land real GitHub PRs, per
   `git-branch-workflow` and `finishing-a-development-branch`. Do not generalize "don't
   push to origin" beyond the child branch this skill is reviewing; a parent/grandparent
   branch that's ready to land is not a case for this skill at all.
2. **Never create commits to make a PR work.** A pull request is a server-side
   comparison of two refs that already exist. If the branch has the commits you want
   reviewed, it is ready. Do not commit, amend, rebase, or squash unless asked.
3. **Never persist the token inside the repo.** Not in `.git/config`, not in a remote
   URL, not in any tracked file, not echoed back in a final message. Supply it inline
   on the push command. Caching it *outside* the repo is a decision for the human to
   make (see Token handling).

## Environment

Work out how to reach the forge before anything else — this is where most of the
trouble lives.

| Where you're running | Base URL |
|---|---|
| Same machine as the forge | `http://localhost:<port>` |
| Inside a Docker container, forge on the host | `http://host.docker.internal:<port>` |

**Inside a container, `localhost` is the container itself.** If the forge's port is
published to the host's loopback only, `host.docker.internal` is what Docker Desktop
routes to it. The bridge gateway address (`172.17.0.1`) does **not** work — don't
substitute it.

Preflight before doing anything else:

```bash
curl -s -o /dev/null -w '%{http_code}\n' "$FJ/"
```

Expect `200`. If it fails from inside a container with an egress firewall, the firewall
needs a rule allowing that port to `host.docker.internal`. If such a rule is supposed
to exist and the preflight still fails, the container is probably running an image
built before the rule was added — rebuild rather than working around the firewall.

**Report URLs to the human using the address *their browser* can reach** — normally
`http://localhost:<port>/...`. From inside a container, `host.docker.internal`
resolves differently on the host and will not open.

## Token handling

```bash
FJ=http://host.docker.internal:3000     # or http://localhost:3000
FORGE_USER=<forge username>
```

Ask for the token if you don't have one. Caching it is optional and the human's call —
if they want it cached, put it somewhere that is **outside any git repo and outside any
mount shared with the host**, mode `600`:

```bash
TOKEN_CACHE="$HOME/.config/forgejo/token"
if [ -f "$TOKEN_CACHE" ]; then
  FORGE_TOKEN=$(cat "$TOKEN_CACHE")
else
  read -rsp 'Forge token: ' FORGE_TOKEN; echo
  mkdir -p "$(dirname "$TOKEN_CACHE")"
  umask 077 && printf '%s' "$FORGE_TOKEN" > "$TOKEN_CACHE"
fi
```

A cache like this is a deliberate exception to "never persist secrets," worth making
only because it never touches a repo or crosses back to the host. Don't create one
unprompted.

## Procedure

### 1. Identify the branch pair

Under git-branch-workflow, a child branch is `<parent>--<slug>`, so its base is
everything before the `--`:

```bash
HEAD_BRANCH=$(git rev-parse --abbrev-ref HEAD)
BASE_BRANCH=${HEAD_BRANCH%%--*}
git log --oneline "$BASE_BRANCH..$HEAD_BRANCH"
git diff --stat "$BASE_BRANCH...$HEAD_BRANCH"   # 3 dots = what the PR will show
```

If `$BASE_BRANCH` equals `$HEAD_BRANCH` the branch has no `--`, so ask what the base
should be rather than guessing.

### 2. Make sure the repo exists on the forge

```bash
REPO=$(basename "$(git rev-parse --show-toplevel)")
curl -s -o /dev/null -w '%{http_code}\n' -u "$FORGE_USER:$FORGE_TOKEN" \
  "$FJ/api/v1/repos/$FORGE_USER/$REPO"
```

`200` means it exists. On `404`, create it — **private**, and **not** auto-initialised
(an auto-init commit gives the repo an unrelated history that nothing can merge into):

```bash
curl -s -u "$FORGE_USER:$FORGE_TOKEN" -X POST "$FJ/api/v1/user/repos" \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"$REPO\",\"private\":true,\"auto_init\":false}" | jq -r '.full_name'
```

### 3. Point a `review` remote at the forge

Store it **without credentials**, so no token lands in `.git/config`:

```bash
git remote get-url review >/dev/null 2>&1 \
  && git remote set-url review "$FJ/$FORGE_USER/$REPO.git" \
  || git remote add    review "$FJ/$FORGE_USER/$REPO.git"
```

A repo shared between a host and a container may already carry a remote for the *other*
environment's address (often named `local`). Leave it alone — it is not reachable from
here, and rewriting it breaks the other side.

### 4. Push both branches

The base must exist on the server or the PR has nothing to compare against. Supply the
token inline so it is never persisted:

```bash
git push "$FJ_WITH_CREDS/$FORGE_USER/$REPO.git" "$BASE_BRANCH" "$HEAD_BRANCH"
# where FJ_WITH_CREDS is the base URL with $FORGE_USER:$FORGE_TOKEN@ in the authority
```

Do **not** use `-u`/`--set-upstream`. It would make these branches look like they track
a remote, obscuring which branches are genuinely local-only.

### 5. Open the pull request

The body is the change description from git-branch-workflow's Step 2 review gate — the
same text you would otherwise paste in chat. Write it to a file and send that, rather
than trying to inline multi-paragraph markdown:

```bash
curl -s -u "$FORGE_USER:$FORGE_TOKEN" -X POST \
  "$FJ/api/v1/repos/$FORGE_USER/$REPO/pulls" \
  -H 'Content-Type: application/json' \
  -d "$(jq -n --arg h "$HEAD_BRANCH" --arg b "$BASE_BRANCH" \
              --arg t "$TITLE" --rawfile body "$BODY_FILE" \
        '{head:$h, base:$b, title:$t, body:$body}')" \
  | jq -r '"PR #\(.number)  \(.html_url)  +\(.additions) -\(.deletions) in \(.changed_files) files"'
```

Set `TITLE` from the branch's actual commits.

### 6. Verify before reporting

```bash
curl -s -u "$FORGE_USER:$FORGE_TOKEN" "$FJ/api/v1/repos/$FORGE_USER/$REPO/pulls/<N>" \
  | jq -r '"mergeable=\(.mergeable) state=\(.state) files=\(.changed_files)"'
```

`mergeable: false` usually means a **real conflict with the base**, not a broken setup.
Confirm locally before reporting it as either:

```bash
git merge-tree --write-tree "$BASE_BRANCH" "$HEAD_BRANCH" >/dev/null 2>&1 \
  && echo "clean" || echo "genuine conflict with base"
```

Then hand the PR URL to the human and **stop**. This is git-branch-workflow's review
gate — it is a hard gate. Do not squash-merge on your own judgement that it looks fine.

**If you are a developer agent under parallel-development**, "hand it to the human"
means `SendMessage` the PR URL to the core agent (`main`) and stop — the core agent
is what actually shows it to the human and relays the approval back.

## After approval

Approval on the local PR is approval for Step 2.6's squash-merge. The child branch is
then deleted locally as usual. The branch left behind on the forge is a review artifact,
not history worth keeping in sync — the durable record is the change description saved
under `docs/development/change/` and the squash commit on the parent.

## Notes

- A private repo returns **404 to unauthenticated clients**, so the web UI shows 404
  until the human logs in. That is not an error.
- The review server being local means *reviewing* sends code nowhere. Your own analysis
  is a different matter: reading files into context sends them to the model API. Do not
  describe this workflow as fully offline.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll push to origin, it's just for review" | `origin` is the public remote. That is the one thing this skill exists to prevent. |
| "The PR needs a commit to have something to show" | A PR compares two existing refs. If the branch has the commits, it is ready. |
| "I'll put the token in the remote URL so pushes just work" | That writes it into `.git/config`, inside the repo. Supply it inline per push. |
| "`mergeable: false` means I set it up wrong" | It usually means a genuine conflict with the base. Verify locally before reporting either. |
| "The PR is open, so I can merge once tests pass" | The gate is human approval, not green tests. Stop and wait. |
| "No local forge configured, so skip the review gate" | The gate is unconditional. Without a forge, deliver the same description in chat and wait. |
| "No forge was mentioned, so there's probably none" | Run the detection check (above) every time — don't infer "no forge" from silence. A `review` remote or an earlier-declared address means one exists whether or not it comes up again. |
