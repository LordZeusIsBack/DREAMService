from django.apps import AppConfig


class SellerDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "seller_data"

    def ready(self):
        from .utils import signals
