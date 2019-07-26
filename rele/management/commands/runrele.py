import logging
import os
import signal
import time

from django.conf import settings
from django.core.management import BaseCommand

from rele import Worker
import rele

from rele.management.discover import discover_subs_modules

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start subscriber threads to consume Relé topics."

    def handle(self, *args, **options):
        subs = self._autodiscover_subs()
        self.stdout.write(f"Configuring worker with {len(subs)} " f"subscription(s)...")
        for sub in subs:
            self.stdout.write(f"  {sub}")
        worker = Worker(
            subs,
            settings.RELE["GC_PROJECT_ID"],
            settings.RELE["GC_CREDENTIALS"],
            settings.RELE.get(
                "DEFAULT_ACK_DEADLINE", os.environ.get("DEFAULT_ACK_DEADLINE", 60)
            ),
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
            settings.RELE["SUB_PREFIX"],
            settings.RELE.get("FILTER_SUBS_BY"),
        )

    def _wait_forever(self):
        self.stdout.write("Consuming subscriptions...")
        while True:
            time.sleep(1)
