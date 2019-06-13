from django.core.management import BaseCommand
from tabulate import tabulate


class Command(BaseCommand):

    def handle(self, *args, **options):
        headers = ['Topic', 'Subscriber(s)', 'Sub']
        self.stdout.write(tabulate([], headers=headers))
