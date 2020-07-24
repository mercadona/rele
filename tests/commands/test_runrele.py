from unittest.mock import ANY, patch

import pytest
from django.core.management import call_command

from rele import Worker


class TestRunReleCommand:
    @pytest.fixture(autouse=True)
    def worker_wait_forever(self):
        with patch.object(
            Worker, "_wait_forever", return_value=None, autospec=True
        ) as p:
            yield p

    @pytest.fixture
    def mock_worker(self):
        with patch("rele.worker.Worker", autospec=True) as p:
            yield p

    def test_calls_worker_start_and_setup_when_runrele(self, mock_worker):
        call_command("runrele")

        mock_worker.assert_called_with([], "SOME-PROJECT-ID", ANY, 60, 2)
        mock_worker.return_value.run_forever.assert_called_once_with()

    def test_prints_warning_when_conn_max_age_not_set_to_zero(
        self, mock_worker, capsys, settings
    ):
        settings.DATABASES = {"default": {"CONN_MAX_AGE": 1}}
        call_command("runrele")

        out, err = capsys.readouterr()
        assert (
            "WARNING: settings.CONN_MAX_AGE is not set to 0. "
            "This may result in slots for database connections to "
            "be exhausted." in err
        )
        mock_worker.assert_called_with([], "SOME-PROJECT-ID", ANY, 60, 2)
        mock_worker.return_value.run_forever.assert_called_once_with()
