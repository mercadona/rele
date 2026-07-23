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
trusted-publishing environment. Used for `1.17.0b1` (PR #320). Recipe: PR
bumping `rele/__init__.py` to a PEP 440 pre-release (e.g. `1.18.0b1`) with a
`chore:` title (so release-please ignores it), merge, then
`gh workflow run release-please.yml --ref master`. Pre-releases are only
installed with an exact pin (`rele==1.18.0b1`).

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

## History quirks

- PyPI history: 1.16.0 was published without a changelog entry or git tag
  (tags stopped at v1.9.0). CHANGELOG.rst is frozen; CHANGELOG.md is the
  live one.
- The changes between 1.16.0 and the first automated release include
  dropping Python < 3.10 — that release should be at least a minor
  (`release-as` in the config can force a specific version).
