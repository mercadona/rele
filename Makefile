.PHONY: clean-pyc clean-build release docs help
.PHONY: lint test coverage test-codecov
.DEFAULT_GOAL := help

help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc clean-tests

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-tests: ## remove pytest artifacts
	rm -fr .pytest_cache/
	rm -fr htmlcov/

install: ## install the project and every dependency group
	uv sync --all-groups --all-extras

lint: ## check for coding style issues
	uv run black . --check --diff
	uv run isort . --check-only

lint-fix: ## try to automagically fix coding style issues
	uv run black .
	uv run isort .

test: ## run tests quickly with the default Python
	uv run python runtests.py tests

coverage: ## generates codecov report
	uv run coverage run --source rele runtests.py tests
	uv run coverage report -m

release: clean sdist ## package and upload a release
	uv run --group deploy twine upload -u __token__ dist/*

sdist: clean ## package
	uv build
	ls -l dist

build-html-doc: ## builds the project documentation in HTML format
	DJANGO_SETTINGS_MODULE=tests.settings uv run --group docs make html -C docs
	open docs/_build/html/index.html

docker-build:
	docker build -t rele .

docker-test: docker-build
	docker run -it --rm --name rele rele

docker-shell: docker-build
	docker run -it --rm --name rele --volume ${PWD}:/rele rele /bin/bash
