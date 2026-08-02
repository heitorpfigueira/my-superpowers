---
name: local-pull-requests
description: Use when a branch needs pull-request review but must not reach a public remote - child branches under git-branch-workflow, or any code that cannot leave the machine. Opens a GitHub-style PR on a self-hosted Forgejo/Gitea running locally. Optional - if the project has no local forge, git-branch-workflow's review gate falls back to delivering the same description in chat.
---

# Local Pull Requests

## Overview

git-branch-workflow's child branches never reach `origin` — they squash-merge into
their parent and disappear. But its Step 2 review gate is a **hard gate**, and a
one-line "please review" in chat is a poor way to review a real diff. A local forge
closes that gap: a GitHub-style PR, with a file-by-file diff and inline comments, for
a branch that never leaves the machine.

**This skill is optional.** It describes one way to run the review gate, not a
requirement of the workflow. If the project has no local forge configured, the gate
still happens — git-branch-workflow just delivers the same change description in chat
and waits for approval there. **The description is identical either way**; only the
delivery differs.

**Announce at start:** "I'm using the local-pull-requests skill to open this branch for
local review."

## Hard rules

1. **Never push to `origin`.** `origin` is the public remote. The entire point is that
   this code does not go there. Push only to the review remote. If a command you are
   about to run contains `push origin`, stop.
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
