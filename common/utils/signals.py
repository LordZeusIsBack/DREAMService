from django.db.models.signals import post_delete
from django.dispatch import receiver

from buyer_data.models import Buyer, BuyerVerification
from seller_data.models import Seller, SellerVerification


@receiver(post_delete, sender=Buyer)
@receiver(post_delete, sender=Seller)
def delete_user_profile_picture(sender, instance, **kwargs):
    """
    Removes the profile picture file from storage when a Buyer or Seller instance is deleted.
    
    Intended as a Django post-delete signal handler. If the deleted instance has a profile picture, the associated file is deleted from its storage backend.
    """
    if instance.profile_picture:
        try:
            storage = instance.profile_picture.storage
            if storage.exists(instance.profile_picture.name): storage.delete(instance.profile_picture.name)
        except Exception as e: print(f"Error deleting profile picture: {e}")

@receiver(post_delete, sender=BuyerVerification)
@receiver(post_delete, sender=SellerVerification)
def delete_user_verification_documents(sender, instance, **kwargs):
    """
    Deletes Aadhaar card and PAN card files from storage when a user verification instance is deleted.
    
    This function is intended to be used as a Django post-delete signal handler for verification models. It checks for the presence of associated document files and removes them from their respective storage backends if they exist.
    """
    if hasattr(instance, 'aadhaar_card') and instance.aadhaar_card:
        try:
            storage = instance.aadhaar_card.storage
            if storage.exists(instance.aadhaar_card.name): storage.delete(instance.aadhaar_card.name)
        except Exception as e: print(f"Error deleting Aadhaar card: {e}")
    if instance.pan_card:
        try:
            storage = instance.pan_card.storage
            if storage.exists(instance.pan_card.name): storage.delete(instance.pan_card.name)
        except Exception as e: print(f"Error deleting PAN card: {e}")
