import argparse
import logging
import os
import sys

from rele import config, discover, subscription
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
    args = parser.parse_args()

    if args.command == "run":
        settings, module_paths = discover.sub_modules(args.settings)
        configuration = config.setup(settings.RELE if settings else None)
        subs = config.load_subscriptions_from_paths(
            module_paths, configuration.sub_prefix, configuration.filter_by
        )
        create_and_run(subs, configuration)
