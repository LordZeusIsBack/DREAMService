from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from common.models import UserExtensionMixin, VerificationMixin

# Create your models here.
class Seller(User):
    business_name = models.CharField(max_length=100, editable=False)

    def __str__(self): return self.business_name


class SellerVerification(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    gstin = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], unique=True, editable=False)

    def __str__(self): return self.seller.business_name

