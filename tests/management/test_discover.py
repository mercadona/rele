from unittest.mock import patch

import pytest
from django.apps import AppConfig, apps

from rele.management.discover import discover_subs_modules
from tests import sample_app, sample_app_2


class TestDiscoverSubsModules:
    @pytest.fixture
    def mock_apps_modules(self):
        with patch.object(apps, "get_app_configs") as mock:
            mock.return_value = [
                AppConfig("test_app", sample_app),
                AppConfig("test_app_2", sample_app_2),
            ]
            yield mock

    @pytest.mark.usefixtures("mock_apps_modules")
    def test_returns_subs_paths_when_app_found(self):
        paths = discover_subs_modules()

        assert len(paths) == 6
        assert "test_app.infrastructure.subs" in paths
        assert "test_app.subs" in paths
        assert "test_app.another_folder.subs" in paths
        assert "test_app_2.infrastructure.subs" in paths
        assert "test_app_2.a_folder.subs" in paths
        assert "test_app_2.subs" in paths
