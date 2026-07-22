import importlib
import logging
import pkgutil
from importlib.util import find_spec as importlib_find
from types import ModuleType

logger = logging.getLogger(__name__)


def module_has_submodule(package: str, module_name: str) -> bool:
    """
    See if 'module' is in 'package'.
    Taken from https://github.com/django/django/blob/master/django/utils/module_loading.py#L63
    """
    imported_package = importlib.import_module(package)
    package_name = imported_package.__name__
    package_path = imported_package.__path__
    full_module_name = package_name + "." + module_name
    try:
        # find_spec ignores its second argument for absolute module names, so
        # passing __path__ (a list) instead of the str the stubs expect is fine
        return importlib_find(full_module_name, package_path) is not None  # type: ignore[arg-type]
    except (ModuleNotFoundError, AttributeError):
        # When module_name is an invalid dotted path, Python raises
        # ModuleNotFoundError.
        return False


def _import_settings_from_path(path: str | None) -> ModuleType | None:
    if path is not None:
        print(f" * Discovered settings: {path!r}")
        return importlib.import_module(path)
    return None


def sub_modules(
    settings_path: str | None = None,
) -> tuple[ModuleType | None, list[str]]:
    """
    In the current directory, we can traverse all modules and determine if they
    have a settings.py or directory with a subs.py module. If either one of
    those exists, we import it, and return the settings module, and
    paths to the subs file.

    If a settings module is not found, we return None.

    :return: (settings module, List[string: subs module paths])
    """
    module_paths: list[str] = []
    for _, package, is_package in pkgutil.walk_packages(path=["."]):
        if package == "settings":
            settings_path = package
        if is_package and module_has_submodule(package, "subs"):
            module = package + ".subs"
            module_paths.append(module)
            print(f" * Discovered subs module: {module!r}")

    settings = _import_settings_from_path(settings_path)
    return settings, module_paths
