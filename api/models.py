from django.db import models
from django.contrib.auth.models import User

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


class Estate(models.Model):
    picture = models.ImageField(upload_to='pictures/estate', null=True, blank=True)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=120, editable=False)
    pricing = models.FloatField(editable=False)
    description = models.TextField()
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)

    def __str__(self): return self.name
