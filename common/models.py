from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class UserExtensionMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='pictures/seller', null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True


class VerificationMixin(models.Model):
    aadhaar_card = models.ImageField(upload_to='pictures/seller/verification/aadhaar', null=True, blank=True)
    aadhaar_number = models.BigIntegerField(
        validators=[MinValueValidator(10 ** 12), MaxValueValidator(10 ** 13 - 1)],
        unique=True,
        editable=False
    )
    pan_card = models.ImageField(upload_to='pictures/seller/verification/pan', null=True, blank=True)
    pan_number = models.CharField(max_length=10, unique=True, editable=False)

    class Meta:
        abstract = True
