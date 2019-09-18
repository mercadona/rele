import logging
import signal
import time

from django.conf import settings
from django.core.management import BaseCommand

import rele
from rele import Worker
from rele.config import Config

from rele.management.discover import discover_subs_modules

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start subscriber threads to consume messages from Relé topics."
    config = Config(settings.RELE)

    def handle(self, *args, **options):
        if settings.CONN_MAX_AGE != 0:
            self.stdout.write(self.style.WARNING(
                'WARNING: settings.CONN_MAX_AGE is not set to 0. '
                'This may result in slots for database connections to '
                'be exhausted.'
            ))
        subs = self._autodiscover_subs()
        self.stdout.write(
            f"Configuring worker with {len(subs)} " f"subscription(s)..."
        )
        for sub in subs:
            self.stdout.write(f"  {sub}")
        worker = Worker(
            subs,
            self.config.gc_project_id,
            self.config.credentials,
            self.config.ack_deadline,
        )
        worker.setup()
        worker.start()

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, worker.stop)
        signal.signal(signal.SIGTSTP, worker.stop)

        self._wait_forever()

    def _autodiscover_subs(self):
        return rele.config.load_subscriptions_from_paths(
            discover_subs_modules(),
            self.config.sub_prefix,
            settings.RELE.get("FILTER_SUBS_BY"),
        )

    def _wait_forever(self):
        self.stdout.write("Consuming subscriptions...")
        while True:
            time.sleep(1)
