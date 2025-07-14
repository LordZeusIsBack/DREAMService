from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.db.models.signals import post_delete
from seller_data.models import Seller

@receiver(post_delete, sender=Seller)
def delete_seller_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture and default_storage.exists(instance.profile_picture.name): default_storage.delete(instance.profile_picture.name)
