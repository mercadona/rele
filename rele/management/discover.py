import logging
import os
import re

from django.apps import apps

logger = logging.getLogger(__name__)


def collect_subs_paths(folder_path, subfiles, module_name, subs_paths):
    if not subfiles:
        return subs_paths

    file = subfiles.pop()

    if re.match(r"^(subs|subs\.py)$", file):
        subs_paths.append(f"{module_name}.subs")
        logger.debug(" * Discovered subs module: %r" % f"{module_name}.subs")
        return collect_subs_paths(folder_path, subfiles, module_name, subs_paths)

    file_path = f"{folder_path}/{file}"
    if os.path.isdir(file_path) and not re.match(r"^__pycache__$", file):
        files_in_folder = os.listdir(file_path)
        subs_paths = collect_subs_paths(
            file_path,
            files_in_folder,
            f"{module_name}.{file}",
            subs_paths
        )

    return collect_subs_paths(folder_path, subfiles, module_name, subs_paths)


def discover_subs_modules():
    logger.debug("Autodiscovering subs...")
    app_configs = apps.get_app_configs()
    subs_modules = []

    for conf in app_configs:
        conf_path = conf.path
        files_in_folder = os.listdir(conf_path)
        subs_modules += collect_subs_paths(conf_path, files_in_folder, conf.name, [])

    return subs_modules
