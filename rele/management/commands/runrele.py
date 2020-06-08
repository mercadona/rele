import logging

from django.conf import settings
from django.core.management import BaseCommand

from rele import config
from rele.management.discover import discover_subs_modules
from rele.worker import create_and_run

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start subscriber threads to consume messages from Relé topics."
    config = config.Config(settings.RELE)

    def handle(self, *args, **options):
        if all(map(lambda x: x.get("CONN_MAX_AGE"), settings.DATABASES.values())):
            self.stderr.write(
                self.style.WARNING(
                    "WARNING: settings.CONN_MAX_AGE is not set to 0. "
                    "This may result in slots for database connections to "
                    "be exhausted."
                )
            )
        subs = config.load_subscriptions_from_paths(
            discover_subs_modules(), self.config.sub_prefix, self.config.filter_by
        )
        self.stdout.write(f"Configuring worker with {len(subs)} " f"subscription(s)...")
        create_and_run(subs, self.config)
