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
        Return the username of the user associated with this buyer verification.
        """
        return f"{self.buyer.user.username}"

class PurchasedEstate(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='purchased_estates')
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name='purchased_by')
    purchase_date = models.DateTimeField(auto_now_add=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)

    class Meta:
        unique_together = ('buyer', 'estate')
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['buyer', 'purchase_date']),
            models.Index(fields=['estate', 'purchase_date']),
            models.Index(fields=['transaction_id'])
        ]

    def save(self, *args, **kwargs):
        """
        Saves the PurchasedEstate instance, preventing changes to transaction_id after creation.
        
        Raises:
            ValidationError: If an attempt is made to modify transaction_id on an existing record.
        """
        if self.pk:
            original = type(self).objects.get(pk=self.pk)
            if original.transaction_id != self.transaction_id: raise ValidationError('transaction_id cannot be changed once set!')
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string summarizing the buyer's email, estate name, and purchase price.
        """
        return f"{self.buyer.user.email} purchased {self.estate.estate_name} for INR{self.purchase_price}"

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

    def save(self, *args, **kwargs):
        is_new = self._state.adding and not WishlistItem.objects.filter(buyer=self.buyer, estate=self.estate).exists()
        super().save(*args, **kwargs)
        if is_new: EstateMetrics.objects.filter(estate=self.estate).update(bookmarks=models.F('bookmarks') + 1)

    def delete(self, *args, **kwargs):
        updated = EstateMetrics.objects.filter(estate=self.estate).update(bookmarks=models.F('bookmarks') - 1)
        if updated == 0: raise ValidationError("This wishlist item does not exist or has already been removed.")
        super().delete(*args, **kwargs)

    def __str__(self):
        """
        Returns a string summarizing the buyer's email and the name of the bookmarked estate.
        """
        return f"{self.buyer.user.email} bookmarked {self.estate.estate_name}"
