from django.db import models
from common.models import CustomUser, UserExtensionMixin, VerificationMixin

# Create your models here.
class Buyer(UserExtensionMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='buyer')

    def __str__(self): """
Returns the full name of the buyer by combining the associated user's first and last names.
"""
return f"{self.user.first_name} {self.user.last_name}"


class BuyerVerification(VerificationMixin):
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE, related_name='buyerverification')

    def __str__(self): """
Returns the full name of the buyer associated with this verification.
"""
return f"{self.buyer.user.first_name} {self.buyer.user.last_name}"
