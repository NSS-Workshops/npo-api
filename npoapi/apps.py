# npoapi/apps.py

from django.apps import AppConfig


class NpoapiConfig(AppConfig):
    name = "npoapi"

    def ready(self):
        import npoapi.signals  # Register the signals
