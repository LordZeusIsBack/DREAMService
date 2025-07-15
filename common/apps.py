from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

    def ready(self):
        """
        Registers signal handlers for the application when the app is ready.
        """
        from .utils import signals