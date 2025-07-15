from django.core.files.storage import default_storage
from django.db.models.signals import post_delete
from django.dispatch import receiver
from estate_data.models import EstateImage

@receiver(post_delete, sender=EstateImage)
def delete_estate_image(sender, instance, **kwargs):
    """
    Deletes the image file associated with an EstateImage instance when it is deleted.
    
    This signal handler ensures that the image file is removed from storage if it exists after the corresponding EstateImage model instance is deleted.
    """
    if instance.image and default_storage.exists(instance.image.name): default_storage.delete(instance.image.name)
