import subprocess
from unittest.mock import patch, ANY

import pytest

from rele import Worker


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
        subprocess.run(["rele-cli", "run", "--settings", "tests.settings", "--third-party-subscriptions", "sample_pypi_package.subs"])

        mock_worker.assert_called_with(
            [], "rele-test", ANY, "europe-west1", 60, 2, None
        )
