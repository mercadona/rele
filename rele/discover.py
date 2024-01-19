import importlib
import logging
import os
import pkgutil
import sys
from importlib.util import find_spec as importlib_find

logger = logging.getLogger(__name__)


def module_has_submodule(package, module_name):
    """
    See if 'module' is in 'package'.
    Taken from https://github.com/django/django/blob/master/django/utils/module_loading.py#L63
    """
    imported_package = importlib.import_module(package)
    package_name = imported_package.__name__
    package_path = imported_package.__path__
    full_module_name = package_name + "." + module_name
    try:
        return importlib_find(full_module_name, package_path) is not None
    except (ModuleNotFoundError, AttributeError):
        # When module_name is an invalid dotted path, Python raises
        # ModuleNotFoundError.
        return False


def _import_settings_from_path(path):
    if path is not None:
        print(" * Discovered settings: %r" % path)
        return importlib.import_module(path)


def sub_modules(settings_path=None, additional_packages=None):
    """
    In the current python path, we can traverse all modules and determine if they
    have a settings.py or directory with a subs.py module. If either one of
    those exists, we import it, and return the settings module, and
    paths to the subs file.

    If a settings module is not found, we return None.

    :return: (settings module, List[string: subs module paths])
    """

    module_paths = []
    for f, package, is_package in pkgutil.walk_packages(path=["."]):
        if package == "settings":
            settings_path = package
        if is_package and module_has_submodule(package, "subs"):
            module = package + ".subs"
            module_paths.append(module)
            print(" * Discovered subs module: %r" % module)

    settings = _import_settings_from_path(settings_path)

    if additional_packages is not None:
        additional_subscription_paths = _discover_subs_from_package(additional_packages)
        module_paths = module_paths + additional_subscription_paths

    return settings, module_paths


def _discover_subs_from_package(packages):
    discoverable_paths = []
    for package_name in packages:
        package_path = _get_package_path(package_name)
        if package_path is not None:
            discoverable_paths.append(package_path)

    module_paths = []
    for f, package, is_package in pkgutil.walk_packages(path=discoverable_paths):
        if is_package and module_has_submodule(package, "subs"):
            module = package + ".subs"
            module_paths.append(module)
            print(" * Discovered subs module: %r" % module)
    return module_paths


def _get_package_path(package_name):
    module_path = None
    try:
        module = importlib.import_module(package_name)
        module_path = os.path.dirname(module.__path__[0])
    except ModuleNotFoundError:
        pass

    return module_path
