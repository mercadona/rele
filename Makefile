.PHONY: clean-pyc clean-build docs help
.DEFAULT_GOAL := help

help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint: ## check style with flake8
	flake8 pubsub tests

test: ## run tests quickly with the default Python
	python runtests.py tests

coverage: ## check code coverage quickly with the default Python
	coverage run --source rele runtests.py tests
	coverage report -m
	coverage html
	open htmlcov/index.html

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

install-dev-requirements:
	pip install -r requirements/base.txt
	pip install -r requirements/test.txt
	pip install -r requirements/docs.txt


build-html-doc:
	DJANGO_SETTINGS_MODULE=tests.settings make html -C docs
