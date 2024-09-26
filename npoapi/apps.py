# apps.py

from django.apps import AppConfig


class NpoapiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "npoapi"

    def ready(self):
        pass  # Remove signal imports if no longer needed
