from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Seller(User):
    profile_picture = models.ImageField(upload_to='pictures/seller', null=True, blank=True)
    business_name = models.CharField(max_length=100, editable=False)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True, editable=False)
    is_verified = models.BooleanField(default=False, editable=False)

    def __str__(self): return self.business_name


class SellerVerification(models.Model):
    aadhaar_card = models.ImageField(upload_to='pictures/seller/verification/aadhaar', null=True, blank=True)
    aadhaar_number = models.BigIntegerField(validators=[MinValueValidator(10 ** 12), MaxValueValidator(10 ** 13 - 1)], unique=True, editable=False)
    pan_card = models.ImageField(upload_to='pictures/seller/verification/pan', null=True, blank=True)
    pan_number = models.CharField(max_length=10, unique=True, editable=False)
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    gstin = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], unique=True, editable=False)

    def __str__(self): return self.seller.business_name

