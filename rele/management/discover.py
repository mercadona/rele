import logging

from django.apps import apps
from django.utils.module_loading import module_has_submodule

logger = logging.getLogger(__name__)


def discover_subs_modules():
    logger.debug("Autodiscovering subs...")
    app_configs = apps.get_app_configs()
    subs_modules = []
    for conf in app_configs:
        if module_has_submodule(conf.module, "subs"):
            module = conf.name + ".subs"
            subs_modules.append(module)
            logger.debug(" * Discovered subs module: %r" % module)
    return subs_modules
