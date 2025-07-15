from django.apps import AppConfig


class EstateDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "estate_data"

    def ready(self):
        """
        Imports application signal handlers when the Django app is fully loaded.
        """
        from .utils import signals
