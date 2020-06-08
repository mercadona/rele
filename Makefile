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

lint: ## check style with flake8
	black . --check --diff
	isort

test: ## run tests quickly with the default Python
	python runtests.py tests

coverage: ## generates codecov report
	coverage run --source rele runtests.py tests
	coverage report -m

release: clean install-deploy-requirements sdist ## package and upload a release
	twine upload -u mercadonatech dist/*

sdist: clean ## package
	python setup.py sdist
	ls -l dist

install-requirements: ## install package requirements
	pip install -r requirements/base.txt

install-test-requirements: ## install requirements for testing
	pip install -r requirements/test.txt

install-deploy-requirements:  ## install requirements for deployment
	pip install -r requirements/deploy.txt

install-docs-requirements:  ## install requirements for documentation
	pip install -r requirements/docs.txt

install-django-requirements: ## install django requirements
	pip install -r requirements/django.txt

install-dev-requirements: install-requirements install-test-requirements install-docs-requirements install-django-requirements

build-html-doc: ## builds the project documentation in HTML format
	DJANGO_SETTINGS_MODULE=tests.settings make html -C docs
	open docs/_build/html/index.html

docker-build:
	docker build -t rele .

docker-test: docker-build
	docker run -it --rm --name rele rele

docker-shell: docker-build
	docker run -it --rm --name rele --volume ${PWD}:/rele rele /bin/bash
