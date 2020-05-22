import argparse
import logging
from pathlib import Path

from rele import config
from rele.cli import autodiscover_subs, create_worker

logger = logging.getLogger(__name__)


def main():
    print(f'Welcome to Relé {__package__}')
    parser = argparse.ArgumentParser(description='Run Relé.')
    parser.add_argument('settings_path', type=str,
                        help='Path to settings file')
    args = parser.parse_args()
    print(f'Settings path {args.settings_path}')
    settings = __import__(args.settings_path)
    breakpoint()
    sub_paths = []
    for path in Path(settings.BASE_DIR).rglob('*subs'):
        import_path = str(path.relative_to(settings.BASE_DIR))
        if 'subs' in import_path:
            path_list = import_path.split('.')
            path_list.pop()
            sub_paths.append(path_list[0].replace('/', '.'))
    breakpoint()
    c = config.setup(settings.RELE)
    s = autodiscover_subs(sub_paths, settings, c)
    create_worker(s, c)
