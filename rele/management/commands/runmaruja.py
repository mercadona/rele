import importlib
import logging
import signal
import time

from django.apps import apps
from django.core.management import BaseCommand
from django.utils.module_loading import module_has_submodule

from rele import Subscription, Worker

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start subscriber threads to consume rele topics.'

    def handle(self, *args, **options):
        subs = self._autodiscover_subs()
        self.stdout.write(f'Configuring worker with {len(subs)} '
                          f'subscription(s)...')
        for sub in subs:
            self.stdout.write(f'  {sub}')
        worker = Worker(subs)
        worker.setup()
        worker.start()

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, worker.stop)
        signal.signal(signal.SIGTSTP, worker.stop)

        self._wait_forever()

    def _discover_subs_modules(self):
        logger.debug('Autodiscovering subs...')
        app_configs = apps.get_app_configs()
        subs_modules = []
        for conf in app_configs:
            if module_has_submodule(conf.module, "subs"):
                module = conf.name + ".subs"
                subs_modules.append(module)
                self.stdout.write(" * Discovered subs module: %r" % module)
        return subs_modules

    def _autodiscover_subs(self):
        subscriptions = []
        for sub_module_path in self._discover_subs_modules():
            sub_module = importlib.import_module(sub_module_path)
            for attr_name in dir(sub_module):
                attribute = getattr(sub_module, attr_name)
                if isinstance(attribute, Subscription):
                    subscriptions.append(attribute)
        return subscriptions

    def _wait_forever(self):
        self.stdout.write('Consuming subscriptions...')
        while True:
            time.sleep(1)
