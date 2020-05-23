import argparse
import logging
import os
import pkgutil
import sys
from pathlib import Path
from importlib.util import find_spec as importlib_find

from rele import config
from rele.cli import autodiscover_subs, create_worker

logger = logging.getLogger(__name__)

def module_has_submodule(package, module_name):
    """See if 'module' is in 'package'."""
    package = __import__(package)
    try:
        package_name = package.__name__
        package_path = package.__path__
    except AttributeError:
        # package isn't a package.
        return False

    full_module_name = package_name + '.' + module_name
    try:
        return importlib_find(full_module_name, package_path) is not None
    except (ModuleNotFoundError, AttributeError):
        # When module_name is an invalid dotted path, Python raises
        # ModuleNotFoundError. AttributeError is raised on PY36 (fixed in PY37)
        # if the penultimate part of the path is not a package.
        return False


def main():
    print(f'Welcome to Relé {__package__}')
    parser = argparse.ArgumentParser(description='Run Relé.')
    sys.path.append('.')

    settings = None
    sub_paths = []
    for file, package, is_package in pkgutil.iter_modules(path=['.']):
        if package == 'settings':
            settings = __import__(package)
        if is_package and module_has_submodule(package, "subs"):
            module = package + ".subs"
            sub_paths.append(module)
            print(f'Found sub: {sub_paths}')
    if settings is None:
        raise ValueError('You must create a settings file in your PYTHONPATH')
    c = config.setup(settings.RELE)
    s = autodiscover_subs(sub_paths, settings, c)
    create_worker(s, c)
