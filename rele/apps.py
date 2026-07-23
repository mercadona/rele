from django.apps import AppConfig
from django.conf import settings

import rele.config


class ReleConfig(AppConfig):
    name = "rele"

    def ready(self) -> None:
        rele.config.setup(settings.RELE)
