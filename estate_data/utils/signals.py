from django.db.models.signals import post_delete
from django.dispatch import receiver

from estate_data.models import EstateImage


@receiver(post_delete, sender=EstateImage)
def remove_estate_images_on_delete(sender, instance, **kwargs):
    """
    Deletes the image file associated with an EstateImage instance when it is deleted.
    
    If the EstateImage instance has an image, this function attempts to remove the image file from its storage backend after verifying its existence. Any errors encountered during deletion are caught and logged.
    """
    if instance.image:
        try:
            storage = instance.image.storage
            if storage.exists(instance.image.name): storage.delete(instance.image.name)
        except Exception as e: print(f"Error deleting image {instance.image.name}: {e}")
