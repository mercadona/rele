import logging
import pkgutil
from importlib.util import find_spec as importlib_find

logger = logging.getLogger(__name__)


def module_has_submodule(package, module_name):
    """See if 'module' is in 'package'."""
    package = __import__(package)
    package_name = package.__name__
    package_path = package.__path__
    full_module_name = package_name + "." + module_name

    try:
        return importlib_find(full_module_name, package_path) is not None
    except (ModuleNotFoundError, AttributeError):
        # When module_name is an invalid dotted path, Python raises
        # ModuleNotFoundError.
        return False


def sub_modules():
    """
    In the current PYTHONPATH, we can traverse all modules and determine if they
    have a settings.py or directory with a subs.py module. If either one of
    those exists, we import it, and return the settings module, and
    paths to the subs file.

    :return: settings module, array of subs module paths.
    """
    settings = None
    module_paths = []
    for f, package, is_package in pkgutil.iter_modules(path=["."]):
        if package == "settings":
            settings = __import__(package)
        if is_package and module_has_submodule(package, "subs"):
            module = package + ".subs"
            module_paths.append(module)
            logger.debug(" * Discovered subs module: %r" % module)
    return settings, module_paths
