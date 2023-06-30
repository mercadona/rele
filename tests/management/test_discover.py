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
    def test_returns_settings_and_paths_when_settings_found(self):
        paths = discover_subs_modules()
        # habrá que crear las carpetas y luego eliminarlas ya que las subs de test no sirve porque test no es una app y por eso seguramente no tenía tests
        assert paths == ["rele.subs", "rele.more_subs.subs", "tests.example_app.subs"]
