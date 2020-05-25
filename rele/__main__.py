import argparse
import logging
import os
import sys

from rele import config, discover

from rele.cli import autodiscover_subs, create_and_run_worker

logger = logging.getLogger(__name__)


def main():
    # modify path so we can import modules and packages
    sys.path.insert(0, os.getcwd())

    parser = argparse.ArgumentParser(
        prog='Relé',
        description='Unharness the power of Relé from the command line')

    subparsers = parser.add_subparsers(help='Select a command', dest='command')

    run_parser = subparsers.add_parser(
        'run',
        help='Run a Relé worker with auto-discovery of subs modules in the '
             'current path. Auto-discovery will include all subs '
             'and settings modules. If no settings module is discovered, '
             'defaults will be used.')

    args = parser.parse_args()

    if args.command == 'run':
        settings, module_paths = discover.sub_modules()
        configuration = config.setup(settings.RELE if settings else None)
        subs = autodiscover_subs(module_paths, configuration)
        create_and_run_worker(subs, configuration)

