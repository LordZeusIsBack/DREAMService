from django.db import models
from django.contrib.auth.models import User
from common.models import UserExtensionMixin, VerificationMixin

# Create your models here.
class Buyer(User, UserExtensionMixin):

    def __str__(self): return f"{self.first_name} {self.last_name}"


class BuyerVerification(VerificationMixin):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)

    def __str__(self): return f"{self.buyer.first_name} {self.buyer.last_name}"
