from django.db import models
from common.models import CustomUser, UserExtensionMixin, VerificationMixin
from estate_data.models import Estate

# Create your models here.
class Buyer(UserExtensionMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='buyer')

    def __str__(self): return f"{self.user.first_name} {self.user.last_name}"


class BuyerVerification(VerificationMixin):
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE, related_name='buyerverification')

    def __str__(self): return f"{self.buyer.user.first_name} {self.buyer.user.last_name}"

class PurchasedEstate(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='purchased_estates')
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name='purchased_by')
    purchase_date = models.DateTimeField(auto_now_add=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, editable=False)

    class Meta:
        unique_together = ('buyer', 'estate')
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['buyer', 'purchase_date']),
            models.Index(fields=['estate', 'purchase_date']),
            models.Index(fields=['transaction_id'])
        ]

    def __str__(self): return f"{self.buyer.user.email} purchased {self.estate.estate_name} for INR{self.purchase_price}"

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

    def __str__(self): return f"{self.buyer.user.email} bookmarked {self.estate.estate_name}"
