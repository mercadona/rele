from unittest.mock import patch
from django.apps import AppConfig, apps
from rele.management.discover import discover_subs_modules
import pytest
from tests import sample_app

class TestDiscoverSubsModules:
    @pytest.fixture
    def mock_apps_modules(self):
        with patch.object(apps, 'get_app_configs') as mock:
            mock.return_value = [AppConfig("test_app", sample_app)]
            yield mock

    @pytest.mark.usefixtures("mock_apps_modules")
    def test_returns_subs_paths_when_app_found(self):
        paths = discover_subs_modules()

        assert paths == ["test_app.infrastructure.subs", "test_app.subs"]
