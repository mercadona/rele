import argparse
import importlib
import logging
import os
import sys

from rele import config, discover
from rele.worker import create_and_run

logger = logging.getLogger(__name__)


def main():
    # modify path so we can import modules and packages
    sys.path.insert(0, os.getcwd())

    parser = argparse.ArgumentParser(
        prog="Relé", description="Harness the power of Relé from the command line"
    )

    subparsers = parser.add_subparsers(help="Select a command", dest="command")

    run_parser = subparsers.add_parser(
        "run",
        help="Run a Relé worker with auto-discovery of subs modules in the "
        "current path. Auto-discovery will include all subs "
        "and settings modules. If no settings module is discovered, "
        "defaults will be used.",
    )
    run_parser.add_argument(
        "--settings",
        "-s",
        default=None,
        required=False,
        help="Settings file dot path. Ex. project.settings. "
        "If none is supplied, Relé will attempt to autodiscover in the root path.",
    )
    run_parser.add_argument(
        "--third-party-subscriptions",
        default=None,
        required=False,
        nargs="+",
        help="Specify subscriptions from the third-party packages. "
        "Example --third-party-subscriptions my_package.subs another_package.subs",
    )
    args = parser.parse_args()

    if args.command == "run":
        run_worker(args.settings, args.third_party_subscriptions)


def run_worker(settings, third_party_subs):
    settings, module_paths = discover.sub_modules(settings)

    if third_party_subs:
        validated_third_party_subs = _validated_third_party_subs(third_party_subs)
        module_paths = module_paths + validated_third_party_subs

    configuration = config.setup(settings.RELE if settings else None)
    subs = config.load_subscriptions_from_paths(
        module_paths, configuration.sub_prefix, configuration.filter_by
    )
    create_and_run(subs, configuration)


def _validated_third_party_subs(subs_import_path):
    validated_subs = []
    for sub_path in subs_import_path:
        if _is_valid_module(sub_path):
            validated_subs.append(sub_path)

    return validated_subs


def _is_valid_module(import_path):
    is_valid = False
    try:
        importlib.import_module(import_path)
        is_valid = True
    except ModuleNotFoundError:
        pass

    return is_valid
