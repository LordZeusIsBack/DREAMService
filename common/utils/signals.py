from django.db.models.signals import post_delete
from django.dispatch import receiver

from buyer_data.models import Buyer, BuyerVerification
from seller_data.models import Seller, SellerVerification


@receiver(post_delete, sender=Buyer)
@receiver(post_delete, sender=Seller)
def delete_user_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:
        try:
            storage = instance.profile_picture.storage
            print(storage)
            if storage.exists(instance.profile_picture.name): storage.delete(instance.profile_picture.name)
        except Exception as e: print(f"Error deleting profile picture: {e}")

@receiver(post_delete, sender=BuyerVerification)
@receiver(post_delete, sender=SellerVerification)
def delete_user_verification_documents(sender, instance, **kwargs):
    if instance.aadhaar_card and default_storage.exists(instance.aadhaar_card.name): default_storage.delete(instance.aadhaar_card.name)
    if instance.pan_card and default_storage.exists(instance.pan_card.name): default_storage.delete(instance.pan_card.name)
