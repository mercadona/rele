from unittest.mock import patch

from django.core.management import call_command

from rele.management.commands.runrele import Command


class TestRunReleCommand:
    @patch.object(Command, "_wait_forever", return_value=None)
    @patch("rele.management.commands.runrele.Worker", autospec=True)
    def test_calls_worker_start_and_setup_when_runrele(
        self, mock_worker, mock_wait_forever
    ):
        call_command("runrele")

        mock_worker.return_value.setup.assert_called()
        mock_worker.return_value.start.assert_called()
