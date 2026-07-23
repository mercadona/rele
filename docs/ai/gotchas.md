# rele gotchas

Non-obvious facts that cost real debugging time. Read before touching
packaging, CI, linting or the worker.

## Packaging / tooling

- **`.gitignore` ignores ALL dotfiles (`.*`)** with explicit `!` exceptions.
  Any new dotfile (configs, workflows in new dot-dirs) is silently skipped by
  `git add`. This shipped a broken release-please setup once
  (`.release-please-manifest.json` never reached master — PR #319).
- **Version must stay dynamic** (`dynamic = ["version"]` reading
  `rele/__init__.py` via hatchling). A static `[project] version` gets
  recorded in `uv.lock`, and then every release bump breaks
  `uv sync --locked` in CI. Verified empirically; revisit only if uv stops
  checking root-package version staleness.
- Build backend is **hatchling**; the wheel must contain `rele/` +
  `rele/py.typed` and nothing else. A stale local `build/` directory can
  contaminate setuptools-era artifacts — `make clean` before hand-building.
- Linters are **pinned exactly** (ruff, mypy in the `test` group). Unpinned
  formatters once made the CI matrix unsatisfiable: different Python
  versions resolved different black versions with mutually incompatible
  styles. Bump pins deliberately, reformatting in the same PR.
- black's old `# noqa` markers *inside docstrings* worked with flake8 but
  ruff ignores them — long URLs in docstrings go in RST link-target blocks
  instead.

## Code

- `FILTER_SUBS_BY` accepts a single callable **or** an iterable; both
  `Subscription.__init__` and `set_filters` must normalize through
  `_init_filters`. A raw callable stored unnormalized crashes on the first
  message (bug shipped 2020–2026, fixed with mypy's help in #317).
- `UnrecoverableException` violates naming rule N818 on purpose
  (`noqa`): renaming it would break the public API.
- On message failure the `Callback` neither acks nor nacks — redelivery
  relies on ack-deadline expiry. Changing this changes user-visible retry
  semantics (see issues #80/#196 for the ongoing design discussion).
- `Worker.stop()` calls `sys.exit(0)` — it is typed `NoReturn` and tests
  must expect `SystemExit`.
- `worker.check_internet_connection` probes the Pub/Sub `api_endpoint` when
  `CLIENT_OPTIONS` sets one; otherwise www.google.com. Air-gapped/Interconnect
  deployments depend on this.

## Backlog context

- Issue #301 (Dead Letter Policy): external contributor with a working fork
  waiting since Feb 2026; team decision deliberately parked. Don't touch the
  issue without team sign-off.
- Issue #224 (make subscription creation optional / least-privilege) is the
  best-regarded pending feature; absorbed #262.
- `post_publish_failure` only fires on `TimeoutError`, not other publish
  errors (issue #198).
