from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from common.models import UserExtensionMixin, VerificationMixin

# Create your models here.
class Seller(User, UserExtensionMixin):
    business_name = models.CharField(max_length=100)

    def __str__(self): return self.business_name


class SellerVerification(VerificationMixin):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    gstin = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], unique=True, editable=False)

    def __str__(self): return self.seller.business_name
