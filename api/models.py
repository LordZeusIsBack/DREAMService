from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

# Create your models here.
class Seller(User):
    profile_picture = models.ImageField(upload_to='pictures/seller', null=True, blank=True)
    business_name = models.CharField(max_length=100, editable=False)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True, editable=False)
    is_verified = models.BooleanField(default=False, editable=False)

    def __str__(self): return self.business_name


class Buyer(User):
    profile_picture = models.ImageField(upload_to='pictures/buyer', null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True, editable=False)
    is_verified = models.BooleanField(default=False, editable=False)

    def __str__(self): return self.username


class VerificationDetails(models.Model):
    aadhaar_card = models.ImageField(upload_to='pictures/seller/verification/aadhaar', null=True, blank=True)
    aadhaar_number = models.BigIntegerField(validators=[MaxValueValidator(999999999999)], unique=True, editable=False)
    pan_card = models.ImageField(upload_to='pictures/seller/verification/pan', null=True, blank=True)
    pan_number = models.CharField(max_length=10, unique=True, editable=False)

    class Mets:
        abstract = True


class SellerVerification(VerificationDetails):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    gstin = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], unique=True, editable=False)

    def __str__(self): return self.seller.business_name


class BuyerVerification(VerificationDetails):
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE)

    def __str__(self): return self.buyer.username


class Estate(models.Model):
    picture = models.ImageField(upload_to='pictures/estate', null=True, blank=True)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=120, editable=False)
    pricing = models.FloatField(editable=False)
    description = models.TextField()
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)

    def __str__(self): return self.name
