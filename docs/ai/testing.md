# rele test suite

## Running

- `make test` → `uv run python runtests.py tests`. `runtests.py` is a small
  Django-aware pytest wrapper: it sets `DJANGO_SETTINGS_MODULE=tests.settings`
  and patches `ReleConfig.ready` before `django.setup()`.
- `make coverage` mirrors CI's coverage job.
- pytest config lives in `[tool.pytest.ini_options]` in pyproject.toml.

## Layout

- `tests/settings.py` — the `RELE` dict used by fixtures (dummy credentials
  from `tests/dummy-pub-sub-credentials.json`, well-formed but fake).
- `tests/conftest.py` — `config`, `config_with_retry_policy`, `mock_worker`…
- `tests/sample_app*/` — fake Django apps/packages exercising subs discovery;
  their `subs/__init__.py` re-exports use redundant aliases on purpose
  (`import x as x`) so ruff doesn't flag them.
- `tests/sample_pypi_package/` — installable fixture package, wired into the
  test dependency group via `[tool.uv.sources]`.

## Known traps (all bit us at least once)

- **Global publisher singleton**: `rele.publishing._publisher` survives
  between tests. Any test assuming "publisher does not exist" must reset it
  first (`publishing._publisher = None`). pytest 8 changed ordering enough to
  expose tests that skipped this.
- **`mock_consume` must never reach Google**: the fixture in
  `tests/test_worker.py` builds a real `SubscriberClient` pointed at the
  non-routable `client_options={"api_endpoint": "localhost:1"}`. Connection
  errors are retryable so the streaming-pull future stays pending forever
  (real cancel/result semantics, zero network). Do NOT remove that option:
  with a real endpoint, Google's terminal 401 races `worker.stop()` and the
  test becomes flaky on CI (history: issue #311, PRs #310/#315 hit it).
- Tests are exempt from line-length (E501) but not from the rest of ruff.
- mypy does not check `tests/` (config scopes `files = ["rele"]`).
