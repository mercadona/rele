# rele release process

Fully automated since 2026-07 (issue #309 / PR #318). No manual steps, no
long-lived tokens.

## Normal flow

1. PRs merge to `master` with Conventional Commit titles (squash-merge: the
   PR title becomes the commit release-please parses).
2. `release-please.yml` (push trigger) maintains a **release PR** that
   accumulates the version bump and CHANGELOG.md entries.
3. Merging the release PR creates the `vX.Y.Z` tag + GitHub release, and the
   `publish` job builds with `uv build` and uploads to PyPI via **trusted
   publishing** (OIDC; environment `pypi`; publisher bound to owner
   `mercadona`, repo `rele`, workflow `release-please.yml`).

## Pre-releases / manual publishes

`release-please.yml` also has a `workflow_dispatch` trigger: it skips the
release-please job and publishes the selected ref directly through the same
trusted-publishing environment. Used for `1.17.0b1` (PR #320).

Recipe:

1. PR bumping `rele/__init__.py` to a PEP 440 pre-release (e.g. `1.18.0b1`)
   with a `chore:` title, so release-please ignores it.
2. Merge, then `gh workflow run release-please.yml --ref master`.
3. **Immediately open a second `chore:` PR resetting `rele/__init__.py` back
   to the last released version.** Skipping this breaks the next real
   release — see below.

Pre-releases are only installed with an exact pin (`rele==1.18.0b1`), and
`workflow_dispatch` creates no tag or GitHub release, so back-fill those by
hand if you want the pre-release visible on GitHub.

### Why step 3 is mandatory

Leaving a pre-release string in `rele/__init__.py` silently breaks the next
release PR. release-please's generic updater matches the semver prefix
`1.18.0` *inside* `1.18.0b1` and rewrites it with the same `1.18.0`, so the
`b1` suffix survives and the file shows **no diff**. Since hatchling reads the
build version from that file, merging the release PR tags `vX.Y.Z` but builds
the pre-release version, and PyPI rejects it as already existing — burning the
tag without publishing anything. Cost a broken release during 1.17.0
(PRs #325–#327).

Invariant to check before merging any release PR: `rele/__init__.py` and
`.release-please-manifest.json` must agree on the last *released* version, and
the release PR's diff must contain the bump of `rele/__init__.py`.

## Wiring details

- Version is single-sourced in `rele/__init__.py`, marked with
  `# x-release-please-version` (release-please's generic updater rewrites
  that line). The manifest (`.release-please-manifest.json`) tracks the last
  *released* version and is the authority release-please reads.
- `release-please-config.json`: python release type, `bootstrap-sha` pins
  where conventional-commit history starts; older commits are ignored.
- The release PR is created by `GITHUB_TOKEN`, so `pr.yml` CI does **not**
  run on it (GitHub restriction). It only touches version + changelog.
- Requires the org/repo Actions setting "Allow GitHub Actions to create and
  approve pull requests" to stay enabled.
- release-please **does not refresh an existing release PR** when the target
  version and changelog are unchanged — it compares those, not the tree. A
  release PR branched off an older master therefore keeps stale file contents
  indefinitely. To force a regeneration: close the PR, delete its branch, then
  re-run the workflow (`gh run rerun <id>`); it recreates the PR from current
  master.
- `release-as` is a **one-shot override**: remove it in the same breath as the
  release it forced. Left in place, the next push targets a version that is
  already tagged.

## History quirks

- Tag naming is inconsistent across history: `v1.4.1` … `v1.15.3` carry the
  `v`, then **`1.16.0` does not** (it points at `0a38df7`), then `v1.17.0`
  onwards does again — that is what `include-v-in-tag` now pins. 1.16.0 was
  published to PyPI without a changelog entry. CHANGELOG.rst is frozen;
  CHANGELOG.md is the live one.
- **1.17.0** (2026-08-05) was the first automated release. Its changelog had
  to be **backfilled by hand** — a deliberate, documented exception to the
  "never edit CHANGELOG.md" rule (PR #327). Cause: the modernization work
  (#303, #310, #312–#318) uses the legacy `[Added]`/`[Changed]`/`[Fixed]`
  prefixes, so release-please skipped every one of those commits — no
  changelog entry *and* no version bump. It saw only the two `docs:` commits
  (#321, #322), proposed a **patch** (1.16.1), and generated a
  documentation-only changelog omitting the headline breaking change
  (dropping Python 3.8/3.9). `release-as: "1.17.0"` forced the version (#324)
  and was removed once it shipped (#327). Hand-edits to past sections are
  safe — release-please only *prepends* new version sections.
  Note `bootstrap-sha` was **not** the operative cause here: release-please
  anchored on the existing `1.16.0` tag (hence the `1.16.0...v1.17.0` compare
  link), so those commits were inside the range it scanned and were dropped
  purely on their titles. `bootstrap-sha` only applies when no prior release
  tag is found.
