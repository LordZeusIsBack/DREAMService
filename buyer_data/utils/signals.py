from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from buyer_data.models import WishlistItem, Buyer
from estate_data.models import EstateMetrics


@receiver(post_save, sender=WishlistItem)
def increment_bookmarks(sender, instance, created, **kwargs):
    """
    Increments the bookmark count for an estate when a new WishlistItem is created.
    
    This function is intended as a Django post_save signal handler for the WishlistItem model. When a WishlistItem is newly created, it atomically increments the `bookmarks` field of the related EstateMetrics record, creating the record if it does not already exist.
    """
    if created:
        with transaction.atomic():
            estate_metrics, _ = EstateMetrics.objects.get_or_create(estate=instance.estate)
            EstateMetrics.objects.select_for_update().filter(pk=estate_metrics.pk).update(bookmarks=F('bookmarks') + 1)

@receiver(post_delete, sender=WishlistItem)
def decrement_bookmarks(sender, instance, **kwargs):
    """
    Decrements the bookmark count for the estate associated with a deleted WishlistItem.
    
    This function is intended as a Django post_delete signal handler for the WishlistItem model. It atomically decrements the `bookmarks` field of the related EstateMetrics record, ensuring consistency during concurrent updates.
    """
    with transaction.atomic(): EstateMetrics.objects.select_for_update().filter(estate=instance.estate).update(bookmarks=F('bookmarks') - 1)

@receiver(post_delete, sender=Buyer)
def delete_buyer_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture and default_storage.exists(instance.profile_picture.name): default_storage.delete(instance.profile_picture.name)
