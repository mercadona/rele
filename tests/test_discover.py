import pytest

from rele import discover
from tests import settings


class TestDiscoverSubModules:
    def test_returns_settings_and_paths_when_settings_found(self):
        discovered_settings, paths = discover.sub_modules("tests.settings")

        assert discovered_settings is settings
        assert discovered_settings.RELE == settings.RELE
        assert paths == [
            "tests.subs",
            "tests.more_subs.subs",
            "tests.sample_app.subs",
            "tests.sample_app.another_folder.subs",
            "tests.sample_app.infrastructure.subs",
            "tests.sample_app_2.subs",
            "tests.sample_app_2.a_folder.subs",
            "tests.sample_app_2.infrastructure.subs",
        ]

    def test_returns_empty_settings_when_no_settings_module_found(self):
        discovered_settings, paths = discover.sub_modules()

        assert discovered_settings is None
        assert paths == [
            "tests.subs",
            "tests.more_subs.subs",
            "tests.sample_app.subs",
            "tests.sample_app.another_folder.subs",
            "tests.sample_app.infrastructure.subs",
            "tests.sample_app_2.subs",
            "tests.sample_app_2.a_folder.subs",
            "tests.sample_app_2.infrastructure.subs",
        ]

    def test_raises_when_incorrect_path(self):
        incorrect_path = "tests.foo"
        with pytest.raises(ModuleNotFoundError):
            discover.sub_modules(incorrect_path)
