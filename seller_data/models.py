from django.db import models
from django.core.validators import MaxValueValidator
from common.models import CustomUser, UserExtensionMixin, VerificationMixin

# Create your models here.
class Seller(UserExtensionMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='seller')
    business_name = models.CharField(max_length=100, editable=False)

    def __str__(self): return self.business_name


class SellerVerification(VerificationMixin):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    agent_rera_id = models.CharField(max_length=12, unique=True, editable=False)
    gstin = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], unique=True, editable=False)

    def __str__(self): return self.seller.business_name
