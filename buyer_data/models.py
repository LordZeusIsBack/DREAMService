from django.db import models
from rest_framework.exceptions import ValidationError
from common.models import CustomUser, UserExtensionMixin, VerificationMixin
from estate_data.models import Estate

# Create your models here.
class Buyer(UserExtensionMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='buyer')

    def __str__(self): return f"{self.user.first_name} {self.user.last_name}"


class BuyerVerification(VerificationMixin):
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE, related_name='buyerverification')

    def __str__(self):
        """
        Return the username of the user linked to this buyer verification instance.
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
