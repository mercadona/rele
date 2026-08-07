import importlib
import sys

import pytest

from rele import discover
from tests import settings


class TestModuleHasSubmodule:
    def test_returns_true_when_the_submodule_exists(self):
        assert discover.module_has_submodule("tests.sample_app", "subs") is True

    def test_returns_false_when_the_submodule_does_not_exist(self):
        assert (
            discover.module_has_submodule("tests.sample_app", "not_a_module") is False
        )

    def test_returns_false_when_the_parent_of_the_dotted_path_is_not_a_package(self):
        # `tests.sample_app.subs` is a plain module, so asking for a submodule of
        # it makes find_spec raise instead of returning None.
        assert discover.module_has_submodule("tests.sample_app", "subs.deeper") is False

    def test_returns_false_when_the_dotted_path_has_a_missing_intermediate_package(
        self,
    ):
        assert discover.module_has_submodule("tests.sample_app", "nope.subs") is False


class TestDiscoverSubModules:
    @pytest.fixture
    def project_with_top_level_settings(self, tmp_path, monkeypatch):
        (tmp_path / "settings.py").write_text(
            'MARKER = "top-level-settings"\nRELE = {}\n'
        )
        package = tmp_path / "autodiscovered_app"
        package.mkdir()
        (package / "__init__.py").write_text("")
        (package / "subs.py").write_text("")

        # A second settings module, addressable by an explicit dotted path, next
        # to the top-level one. It has no subs.py, so it does not change the
        # discovered paths.
        explicit = tmp_path / "explicit_app"
        explicit.mkdir()
        (explicit / "__init__.py").write_text("")
        (explicit / "settings.py").write_text(
            'MARKER = "explicit-settings"\nRELE = {}\n'
        )

        monkeypatch.chdir(tmp_path)
        monkeypatch.syspath_prepend(str(tmp_path))
        sys.path_importer_cache.pop(".", None)
        importlib.invalidate_caches()

        yield tmp_path

        for module_name in (
            "settings",
            "autodiscovered_app.subs",
            "autodiscovered_app",
            "explicit_app.settings",
            "explicit_app",
        ):
            sys.modules.pop(module_name, None)
        sys.path_importer_cache.pop(".", None)
        importlib.invalidate_caches()

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

    @pytest.mark.usefixtures("project_with_top_level_settings")
    def test_autodiscovers_top_level_settings_module_when_no_path_given(self):
        discovered_settings, paths = discover.sub_modules()

        assert discovered_settings is not None
        assert discovered_settings.__name__ == "settings"
        assert discovered_settings.MARKER == "top-level-settings"
        assert discovered_settings is sys.modules["settings"]
        assert paths == ["autodiscovered_app.subs"]

    @pytest.mark.usefixtures("project_with_top_level_settings")
    def test_explicit_settings_path_is_not_overridden_by_autodiscovery(self):
        discovered_settings, paths = discover.sub_modules("explicit_app.settings")

        assert discovered_settings is not None
        assert discovered_settings.__name__ == "explicit_app.settings"
        assert discovered_settings.MARKER == "explicit-settings"
        assert paths == ["autodiscovered_app.subs"]

    def test_raises_when_incorrect_path(self):
        incorrect_path = "tests.foo"
        with pytest.raises(ModuleNotFoundError):
            discover.sub_modules(incorrect_path)
