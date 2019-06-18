from django.apps import apps
from django.utils.module_loading import module_has_submodule


def discover_subs_modules():
    app_configs = apps.get_app_configs()
    subs_modules = []
    for conf in app_configs:
        if module_has_submodule(conf.module, "subs"):
            module = conf.name + ".subs"
            subs_modules.append(module)
    return subs_modules
