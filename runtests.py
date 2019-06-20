#!/usr/bin/env python
# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

import os
import sys

import django
from unittest.mock import patch

from rele.apps import ReleConfig


class PytestTestRunner(object):
    """Runs pytest to discover and run tests."""

    def __init__(self, verbosity=1, failfast=False, keepdb=False, **kwargs):
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb

    def run_tests(self, test_labels):
        """Run pytest and return the exitcode.

        It translates some of Django's test command option to pytest's.
        """
        import pytest

        argv = []
        if self.verbosity == 0:
            argv.append("--quiet")
        if self.verbosity == 2:
            argv.append("--verbose")
        if self.verbosity == 3:
            argv.append("-vv")
        if self.failfast:
            argv.append("--exitfirst")
        if self.keepdb:
            argv.append("--reuse-db")

        argv.extend(test_labels)
        return pytest.main(argv)


def run_tests(*test_args):
    if not test_args:
        test_args = ["tests"]

    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"

    with patch.object(ReleConfig, "ready"):
        django.setup()

    test_runner = PytestTestRunner()
    failures = test_runner.run_tests(test_args)
    sys.exit(bool(failures))


if __name__ == "__main__":
    run_tests(*sys.argv[1:])
