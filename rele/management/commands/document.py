from django.apps import apps
from django.core.management import BaseCommand
from django.utils.module_loading import module_has_submodule
from tabulate import tabulate

from rele.config import load_subscriptions_from_paths


def discover_subs_modules():
    app_configs = apps.get_app_configs()
    subs_modules = []
    for conf in app_configs:
        if module_has_submodule(conf.module, "subs"):
            module = conf.name + ".subs"
            subs_modules.append(module)
    return subs_modules


class Command(BaseCommand):

    def handle(self, *args, **options):
        headers = ['Topic', 'Subscriber(s)', 'Sub']

        subscription_paths = discover_subs_modules()
        subs = sorted(load_subscriptions_from_paths(subscription_paths),
                      key=lambda sub: sub.topic)
        sub_data = [(sub.topic, sub.name, sub._func.__name__) for sub in subs]

        self.stdout.write(tabulate(sub_data, headers=headers))
