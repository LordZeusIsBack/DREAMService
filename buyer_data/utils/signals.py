from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from buyer_data.models import WishlistItem
from estate_data.models import EstateMetrics


@receiver(post_save, sender=WishlistItem)
def increment_bookmarks(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            estate_metrics, _ = EstateMetrics.objects.get_or_create(estate=instance.estate)
            EstateMetrics.objects.select_for_update().filter(pk=estate_metrics.pk).update(bookmarks=F('bookmarks') + 1)

@receiver(post_delete, sender=WishlistItem)
def decrement_bookmarks(sender, instance, **kwargs):
    with transaction.atomic(): EstateMetrics.objects.select_for_update().filter(estate=instance.estate).update(bookmarks=F('bookmarks') - 1)
