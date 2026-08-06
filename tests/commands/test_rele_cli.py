import sys
from unittest.mock import patch

import pytest

from rele.__main__ import main, run_worker


class TestReleCli:
    def test_rele_cli_run(self, mock_worker):
        run_worker("tests.settings", ["sample_pypi_package.subs"])
        worker_subscriptions_argument = mock_worker.mock_calls[0].args[0]
        topic_names = [sub.name for sub in worker_subscriptions_argument]

        assert "rele-topic-from-third-party-package" in topic_names

    def test_ignores_non_valid_third_party_subs(self, mock_worker):
        run_worker("tests.settings", ["sample_pypi_package.no_subs"])

        mock_worker.assert_called()


class TestReleCliMain:
    @pytest.fixture(autouse=True)
    def restore_sys_path(self):
        original_path = sys.path[:]
        yield
        sys.path[:] = original_path

    @pytest.fixture
    def mock_run_worker(self):
        with patch("rele.__main__.run_worker", autospec=True) as p:
            yield p

    def test_parses_long_settings_flag(self, mock_run_worker):
        with patch.object(
            sys, "argv", ["rele-cli", "run", "--settings", "foo.settings"]
        ):
            main()

        mock_run_worker.assert_called_once_with("foo.settings", None)

    def test_parses_short_settings_flag(self, mock_run_worker):
        with patch.object(sys, "argv", ["rele-cli", "run", "-s", "foo.settings"]):
            main()

        mock_run_worker.assert_called_once_with("foo.settings", None)

    def test_parses_multiple_third_party_subscriptions(self, mock_run_worker):
        with patch.object(
            sys,
            "argv",
            [
                "rele-cli",
                "run",
                "--settings",
                "foo.settings",
                "--third-party-subscriptions",
                "my_package.subs",
                "another_package.subs",
            ],
        ):
            main()

        mock_run_worker.assert_called_once_with(
            "foo.settings", ["my_package.subs", "another_package.subs"]
        )

    def test_parses_single_third_party_subscription(self, mock_run_worker):
        with patch.object(
            sys,
            "argv",
            ["rele-cli", "run", "--third-party-subscriptions", "my_package.subs"],
        ):
            main()

        mock_run_worker.assert_called_once_with(None, ["my_package.subs"])

    def test_defaults_to_none_when_no_flags_are_supplied(self, mock_run_worker):
        with patch.object(sys, "argv", ["rele-cli", "run"]):
            main()

        mock_run_worker.assert_called_once_with(None, None)

    def test_third_party_subscriptions_requires_at_least_one_value(
        self, mock_run_worker
    ):
        with patch.object(
            sys, "argv", ["rele-cli", "run", "--third-party-subscriptions"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 2
        mock_run_worker.assert_not_called()

    def test_does_not_run_worker_when_no_command_is_given(self, mock_run_worker):
        with patch.object(sys, "argv", ["rele-cli"]):
            main()

        mock_run_worker.assert_not_called()

    def test_exits_when_command_is_unknown(self, mock_run_worker):
        with patch.object(sys, "argv", ["rele-cli", "walk"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 2
        mock_run_worker.assert_not_called()

    def test_prepends_current_working_directory_to_sys_path(self, mock_run_worker):
        cwd = "/tmp/rele-cli-sentinel-cwd"
        with patch("rele.__main__.os.getcwd", return_value=cwd):
            with patch.object(sys, "argv", ["rele-cli", "run"]):
                main()

        assert sys.path[0] == cwd
