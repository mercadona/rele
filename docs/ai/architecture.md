# rele architecture

One-paragraph mental model: users declare subscriptions with the `@sub`
decorator; a `Worker` discovers them, creates/updates the corresponding
Pub/Sub subscriptions on Google, and consumes messages, wrapping every
lifecycle moment in middleware hooks. Publishing goes through a process-wide
`Publisher` singleton.

## Modules (all under `rele/`)

- `subscription.py` — `Subscription` (name = `prefix-topic-suffix`, local
  `filter_by` callables, backend filter, per-sub `RetryPolicy`), the `@sub`
  decorator (validates the callback signature: exactly one positional arg +
  `**kwargs`), and `Callback` (JSON-decodes the message, runs the sub, acks
  on success; on exception it neither acks nor nacks — redelivery happens via
  ack-deadline expiry).
- `client.py` — `Subscriber` (create/update subscriptions, auto-creates
  missing topics, translates rele `RetryPolicy` → gcloud types) and
  `Publisher` (json-encodes with the configured encoder, non-blocking by
  default; only `TimeoutError` triggers the `post_publish_failure` hook —
  known limitation, see issue #198).
- `worker.py` — `Worker` bootstraps consumption per subscription
  (`ThreadScheduler`, `THREADS_PER_SUBSCRIPTION`), restarts done/cancelled
  futures in `_wait_forever`, checks connectivity against the configured
  `api_endpoint` (or www.google.com), and `stop()` exits the process.
  `create_and_run` wires signals (SIGINT/SIGTERM/SIGTSTP).
- `middleware.py` — global `_middlewares` list, `run_middleware_hook`
  dispatch, `BaseMiddleware` with all hook signatures. Implementations in
  `contrib/`: logging (default), verbose logging, Django DB connection
  management, Flask app-context, unrecoverable-exception ack.
- `config.py` — `Config` parses the `RELE` settings dict; `setup()` also
  initializes the global publisher and registers middleware.
  `load_subscriptions_from_paths` imports subs modules and applies global
  prefix/filters.
- `publishing.py` — module-level `_publisher` singleton; `publish()`
  lazy-initializes it via settings discovery if `setup()` was never called.
- `discover.py` — walks the current path for `subs` modules (CLI flow).
- `management/` — Django: `runrele` / `showsubscriptions` commands; discovery
  walks `INSTALLED_APPS` instead of the filesystem.
- `__main__.py` — `rele-cli run`, with `--third-party-subscriptions` for
  pip-installed subs modules.

## Entry points

- Django: add `rele` to `INSTALLED_APPS`, configure `settings.RELE`, run
  `python manage.py runrele`.
- Standalone: `rele-cli run [--settings project.settings]`.

## Key invariants

- `Publisher` must stay a singleton per process (memory leak otherwise).
- Subscription names must be unique; duplicates raise at discovery time.
- Everything importable from `rele/` is public API for downstream services.
