from django.db import models
from common.models import CustomUser, UserExtensionMixin, VerificationMixin

# Create your models here.
class Buyer(UserExtensionMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='buyer_profile')

    def __str__(self): return f"{self.user.first_name} {self.user.last_name}"


class BuyerVerification(VerificationMixin):
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE)

    def __str__(self): return f"{self.buyer.user.first_name} {self.buyer.user.last_name}"
