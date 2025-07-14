from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.db.models.signals import post_delete
from seller_data.models import Seller, SellerVerification

@receiver(post_delete, sender=Seller)
def delete_seller_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture and default_storage.exists(instance.profile_picture.name): default_storage.delete(instance.profile_picture.name)

@receiver(post_delete, sender=SellerVerification)
def delete_seller_verification_picture(sender, instance, **kwargs):
    if instance.aadhaar_card and default_storage.exists(instance.aadhaar_card.name): default_storage.delete(instance.aadhaar_card.name)
    if instance.pan_card and default_storage.exists(instance.pan_card.name): default_storage.delete(instance.pan_card.name)
