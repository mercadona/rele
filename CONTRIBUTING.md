# Contributing

Thank you for contributing to Relé! 

To make the experience as easy as possible, we ask that you follow some simple 
guidelines. Use your best judgment, and feel free to propose changes to this document 
in a pull request. 

Additionally, be sure that you read and follow our 
[Code of Conduct](https://github.com/mercadona/rele/blob/master/CODE_OF_CONDUCT.md). 

## Code

We ask that you start a discussion before attempting to make a code contribution. For feature 
requests, issues, bugs, etc. please 
[create an issue via Github](https://github.com/mercadona/rele/issues/new) where we can all 
discuss the contribution to the project. 

It is always best to have community input before proposing changes that may later be rejected.

### Development setup

The project uses [uv](https://docs.astral.sh/uv/) to manage its environment.
Dependencies are declared in `pyproject.toml` (the `test`, `docs` and `deploy`
dependency groups) and locked in `uv.lock`. After
[installing uv](https://docs.astral.sh/uv/getting-started/installation/), run:

```console
$ make install
```

The Makefile targets (`make test`, `make lint`, ...) run through `uv run`, so
they keep the environment in sync automatically.

### Pull Requests

* Make sure any code changes are covered by tests by running `make test`.
* Run `make lint` on any modified files.
* If your branch is behind master, 
[rebase](https://github.com/edx/edx-platform/wiki/How-to-Rebase-a-Pull-Request) on top of it.
* Include the related issue's number so that Github closes _automagically_ 
when the PR is merged. Example: `Fix #12`
* Add yourself to the [AUTHORS](./AUTHORS.md) file

## Issues

When you open an issue make sure you include the full stack trace and
that you list all pertinent information (operating system, Python implementation, etc.) 
as part of the issue description.

Please include a minimal, reproducible test case with every bug
report.
