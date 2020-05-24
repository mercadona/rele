import logging

from django.conf import settings
from django.core.management import BaseCommand

from rele.cli import create_worker, autodiscover_subs
from rele.config import Config
from rele.management.discover import discover_subs_modules

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start subscriber threads to consume messages from Relé topics."
    config = Config(settings.RELE)

    def handle(self, *args, **options):
        if all(map(lambda x: x.get("CONN_MAX_AGE"), settings.DATABASES.values())):
            self.stderr.write(
                self.style.WARNING(
                    "WARNING: settings.CONN_MAX_AGE is not set to 0. "
                    "This may result in slots for database connections to "
                    "be exhausted."
                )
            )
        subs = autodiscover_subs(discover_subs_modules(), self.config)
        self.stdout.write(f"Configuring worker with {len(subs)} " f"subscription(s)...")
        create_worker(subs, self.config)
