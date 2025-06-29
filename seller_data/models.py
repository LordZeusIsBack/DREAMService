from django.db import models
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError
from common.models import CustomUser, UserExtensionMixin, VerificationMixin

# Create your models here.
class Seller(UserExtensionMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='seller')
    business_name = models.CharField(max_length=100, editable=False)

    def __str__(self): return self.business_name


class SellerVerification(VerificationMixin):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, db_index=True)
    agent_rera_id = models.CharField(max_length=12, unique=True, editable=False)
    gstin = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], unique=True, editable=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        original = type(self).objects.get(pk=self.pk)
        if original.gstin != self.gstin: raise ValidationError('GSTIN cannot be changed once set!')
        if original.agent_rera_id != self.agent_rera_id: return ValidationError('RERA ID cannot be changed once set!')
        return super().save(*args, **kwargs)

    def __str__(self): return self.seller.business_name
