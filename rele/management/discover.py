import logging
import os
import re

from django.apps import apps

logger = logging.getLogger(__name__)


def is_subs_module(file):
    return re.match(r"^(subs|subs\.py)$", file)


def collect_subs_from_path(folder_path, subfiles, module_name, subs_paths):
    if not subfiles:
        return subs_paths

    file = subfiles.pop()

    if is_subs_module(file):
        logger.debug(f" * Discovered subs module: {module_name}.subs")
        subs_module = f"{module_name}.subs"
        if subs_module not in subs_paths:
            subs_paths.append(f"{module_name}.subs")

        return collect_subs_from_path(folder_path, subfiles, module_name, subs_paths)

    file_path = f"{folder_path}/{file}"
    if os.path.isdir(file_path):
        subs_paths = collect_subs_from_path(
            folder_path=file_path,
            subfiles=os.listdir(file_path),
            module_name=f"{module_name}.{file}",
            subs_paths=subs_paths,
        )

    return collect_subs_from_path(folder_path, subfiles, module_name, subs_paths)


def collect_subs_from_app(app_config):
    return collect_subs_from_path(
        folder_path=app_config.path,
        subfiles=os.listdir(app_config.path),
        module_name=app_config.name,
        subs_paths=[],
    )


def discover_subs_modules():
    logger.debug("Autodiscovering subs...")
    app_configs = apps.get_app_configs()
    subs_modules = []

    for app in app_configs:
        subs_modules += collect_subs_from_app(app)

    return subs_modules
