# Changelog

## [1.17.0](https://github.com/mercadona/rele/compare/1.16.0...v1.17.0) (2026-08-05)

First fully automated release, and the first since 1.16.0 (2025-07-25). Ships
the same code as the `1.17.0b1` pre-release plus the two documentation changes
below.

> Every entry except the Documentation ones was **backfilled by hand**. The
> modernization work landed before this repo adopted Conventional Commits (it
> used the legacy `[Added]`/`[Changed]`/`[Fixed]` prefixes) and predates
> `bootstrap-sha`, so release-please could not derive it from the commit
> history and generated a documentation-only changelog.

### ⚠ BREAKING CHANGES

* **Python 3.8 and 3.9 are no longer supported.** `requires-python` moved from
  `>=3.8` to `>=3.10`, and support now extends through Python 3.14. Installing
  on 3.8 or 3.9 fails at dependency resolution instead of at runtime
  ([#312](https://github.com/mercadona/rele/issues/312)) ([da1c36c](https://github.com/mercadona/rele/commit/da1c36c8633868444c2899a27b50882756d5d925))

### Features

* type hints for the public API, checked by mypy strict; `rele/py.typed` ships in the wheel ([#317](https://github.com/mercadona/rele/issues/317)) ([5879fee](https://github.com/mercadona/rele/commit/5879fee5f58ce253244d70e397c86e0aa163a468))
* automate releases with release-please and PyPI trusted publishing ([#318](https://github.com/mercadona/rele/issues/318)) ([5c2ee4a](https://github.com/mercadona/rele/commit/5c2ee4a77af1c1422f94c15019a5460716582050))

### Bug Fixes

* move return out of finally block in `check_internet_connection` ([#303](https://github.com/mercadona/rele/issues/303)) ([3beb3fc](https://github.com/mercadona/rele/commit/3beb3fc7cc21f79db021910b527c4c240bea1a10))
* stop the worker-stop test from racing a real Pub/Sub connection ([#316](https://github.com/mercadona/rele/issues/316)) ([7753e0c](https://github.com/mercadona/rele/commit/7753e0c860fccc54998e3d8b95901d045735b0ec))

### Build System

* move packaging metadata to pyproject.toml ([#310](https://github.com/mercadona/rele/issues/310)) ([30cc7fd](https://github.com/mercadona/rele/commit/30cc7fd0dcb2a28cde47c03eedfcd177c9ff10ec))
* switch build backend to hatchling with SPDX license expression ([#313](https://github.com/mercadona/rele/issues/313)) ([fe0d2d4](https://github.com/mercadona/rele/commit/fe0d2d4c8fbbe20cc198b3cb2dc76d139ab75ba8))
* adopt uv: dependencies live in pyproject.toml, requirements/ removed ([#314](https://github.com/mercadona/rele/issues/314)) ([6a25272](https://github.com/mercadona/rele/commit/6a25272fbae1376415f66e33e4e56d4d73b6e2ac))
* replace black and isort with ruff ([#315](https://github.com/mercadona/rele/issues/315)) ([467de69](https://github.com/mercadona/rele/commit/467de698d5bc41c1dce69ce6d423409231db9dff))

### Documentation

* add AI-ready context files (CLAUDE.md + docs/ai) ([#321](https://github.com/mercadona/rele/issues/321)) ([47658d5](https://github.com/mercadona/rele/commit/47658d50b75f71899aca1fa3df91a11e96cf8667))
* refresh stale documentation ([#322](https://github.com/mercadona/rele/issues/322)) ([d965c7f](https://github.com/mercadona/rele/commit/d965c7f8347afd8016d0a8f71752baee7ad8f85e))
