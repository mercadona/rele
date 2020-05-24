import argparse
import logging
import os
import pkgutil
import sys
from importlib.util import find_spec as importlib_find

from rele import config
from rele.cli import autodiscover_subs, create_worker

logger = logging.getLogger(__name__)


def module_has_submodule(package, module_name):
    """See if 'module' is in 'package'."""
    package = __import__(package)
    package_name = package.__name__
    package_path = package.__path__

    full_module_name = package_name + '.' + module_name
    try:
        return importlib_find(full_module_name, package_path) is not None
    except (ModuleNotFoundError, AttributeError):
        # When module_name is an invalid dotted path, Python raises
        # ModuleNotFoundError.
        return False


def main():
    print(f'Welcome to Relé CLI')
    parser = argparse.ArgumentParser(description='Run Relé.')
    parser.add_argument('run', nargs=1, help='Run a worker.', default='--help')

    # modify path so we can import modules and packages
    sys.path.insert(0, os.getcwd())

    settings = None
    module_paths = []
    for f, package, is_package in pkgutil.iter_modules(path=['.']):
        if package == 'settings':
            settings = __import__(package)
        if is_package and module_has_submodule(package, "subs"):
            module = package + ".subs"
            module_paths.append(module)
            logger.debug(" * Discovered subs module: %r" % module)

    configuration = config.setup(settings.RELE if settings else None)
    subs = autodiscover_subs(module_paths, configuration)
    create_worker(subs, configuration)
