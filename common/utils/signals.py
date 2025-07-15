from django.core.files.storage import default_storage
from django.db.models.signals import post_delete
from django.dispatch import receiver

from buyer_data.models import Buyer
from seller_data.models import Seller


@receiver(post_delete, sender=Buyer)
@receiver(post_delete, sender=Seller)
def delete_user_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture and default_storage.exists(instance.profile_picture.name): default_storage.delete(instance.profile_picture.name)
