from django.db import models
from functools import partial
from common.models import get_verification_document_upload_path
from common.utils.storage_backends import MediaStorage
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.exceptions import ValidationError
from common.models import CustomUser, UserExtensionMixin, VerificationMixin
from estate_data.models import Estate

aadhaar_card_image_path = partial(get_verification_document_upload_path, subfolder='verification/aadhaar_card')

# Create your models here.
class Buyer(UserExtensionMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='buyer')

    def __str__(self): return f"{self.user.first_name} {self.user.last_name}"


class BuyerVerification(VerificationMixin):
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE, related_name='buyerverification')
    aadhaar_card = models.ImageField(upload_to=aadhaar_card_image_path, null=True, blank=True, storage=MediaStorage)
    aadhaar_number = models.BigIntegerField(
        validators=[MinValueValidator(10 ** 12), MaxValueValidator(10 ** 13 - 1)],
        unique=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        """
        Override the save method to prevent changes to Aadhaar number and Aadhaar card image after initial set.
        
        Raises:
            ValidationError: If an attempt is made to modify the Aadhaar number or replace the Aadhaar card image after they have been set.
        """
        if self.pk:
            try:
                original = type(self).objects.get(pk=self.pk)
                if original.aadhaar_number != self.aadhaar_number: raise ValidationError('Aadhaar Number once set cannot be changed!')
                if original.aadhaar_card and self.aadhaar_card:
                    if original.aadhaar_card.name != self.aadhaar_card.name:
                        raise ValidationError('Aadhaar Card once set cannot be changed!')
            except type(self).DoesNotExist: pass
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the username associated with the buyer linked to this verification instance.
        """
        return f"{self.buyer.user.username}"


class WishlistItem(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='wishlistitems')
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'estate')
        ordering = ['-added_on']
        indexes = [
            models.Index(fields=['buyer', 'added_on']),
            models.Index(fields=['estate', 'added_on'])
        ]

    def __str__(self):
        """
        Return a summary string showing the buyer's email and the name of the bookmarked estate.
        """
        return f"{self.buyer.user.email} bookmarked {self.estate.estate_name}"
