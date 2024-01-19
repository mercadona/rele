import subprocess
from unittest.mock import ANY, patch

import pytest

from rele import Worker
from rele.__main__ import run_worker


class TestReleCli:
    @pytest.fixture
    def mock_worker(self):
        with patch("rele.worker.Worker", autospec=True) as p:
            yield p

    @pytest.fixture(autouse=True)
    def worker_wait_forever(self):
        with patch.object(
            Worker, "_wait_forever", return_value=None, autospec=True
        ) as p:
            yield p

    def test_rele_cli_run(self, mock_worker):
        run_worker("tests.settings", ["sample_pypi_package.subs"])
        topic_names = [sub.name for sub in mock_worker.mock_calls[0].args[0]]

        assert "rele-topic-from-third-party-package" in topic_names
