from django.apps import AppConfig


class BuyerDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "buyer_data"

    def ready(self):
        """
        Imports application signal handlers when the Django app is fully loaded.
        """
        from .utils import signals
