from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Buyer(User):
    profile_picture = models.ImageField(upload_to='pictures/seller', null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True, editable=False)
    is_verified = models.BooleanField(default=False, editable=False)

    def __str__(self): return self.first_name + " " + self.last_name


class BuyerVerification(models.Model):
    aadhaar_card = models.ImageField(upload_to='pictures/seller/verification/aadhaar', null=True, blank=True)
    aadhaar_number = models.BigIntegerField(validators=[MinValueValidator(10 ** 12), MaxValueValidator(10 ** 13 - 1)], unique=True, editable=False)
    pan_card = models.ImageField(upload_to='pictures/seller/verification/pan', null=True, blank=True)
    pan_number = models.CharField(max_length=10, unique=True, editable=False)
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE)

    def __str__(self): return self.buyer.first_name + " " + self.buyer.last_name

