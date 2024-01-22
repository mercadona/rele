from rele.__main__ import run_worker


class TestReleCli:
    def test_rele_cli_run(self, mock_worker):
        run_worker("tests.settings", ["sample_pypi_package.subs"])
        worker_subscriptions_argument = mock_worker.mock_calls[0].args[0]
        topic_names = [sub.name for sub in worker_subscriptions_argument]

        assert "rele-topic-from-third-party-package" in topic_names

    def test_ignores_non_valid_third_party_subs(self, mock_worker):
        run_worker("tests.settings", ["sample_pypi_package.no_subs"])

        mock_worker.assert_called()
