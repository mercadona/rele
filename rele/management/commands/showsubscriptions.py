from django.core.management import BaseCommand
from tabulate import tabulate

from rele.config import load_subscriptions_from_paths
from rele.management.discover import discover_subs_modules


class Command(BaseCommand):
    help = "List information about Pub/Sub subscriptions registered using Relé."

    def handle(self, *args, **options):
        headers = ["Topic", "Subscriber(s)", "Sub"]

        subscription_paths = discover_subs_modules()
        subs = sorted(
            load_subscriptions_from_paths(subscription_paths),
            key=lambda sub: sub.topic,
        )
        sub_data = [(sub.topic, sub.name, sub._func.__name__) for sub in subs]

        self.stdout.write(tabulate(sub_data, headers=headers))
