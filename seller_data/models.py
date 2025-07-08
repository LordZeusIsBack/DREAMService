from django.db import models
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError
from common.models import CustomUser, UserExtensionMixin, VerificationMixin

# Create your models here.
class Seller(UserExtensionMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='seller')
    business_name = models.CharField(max_length=100, editable=False)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                original = type(self).objects.get(pk=self.pk)
                if original.business_name != self.business_name: raise ValidationError('Business name cannot be changed once set!')
            except type(self).DoesNotExist: pass
        super().save(*args, **kwargs)

    def __str__(self): return self.business_name


class SellerVerification(VerificationMixin):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, db_index=True)
    agent_rera_id = models.CharField(max_length=12, unique=True, editable=False)
    gstin = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], unique=True, editable=False)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to prevent changes to GSTIN and agent RERA ID after creation.
        
        Raises a ValidationError if an attempt is made to modify the GSTIN. Returns a ValidationError if the agent RERA ID is changed (note: this should typically raise instead of return). Allows normal saving if these fields remain unchanged or if the instance is being created.
        """
        if self.pk:
            try:
                original = type(self).objects.get(pk=self.pk)
                if original.gstin != self.gstin: raise ValidationError('GSTIN cannot be changed once set!')
                if original.agent_rera_id != self.agent_rera_id: return ValidationError('RERA ID cannot be changed once set!')
            except type(self).DoesNotExist: pass
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the business name of the associated seller as the string representation of the SellerVerification instance.
        """
        return self.seller.business_name


class SubscriptionStage(models.TextChoices):
    STAGE_1 = '1', 'Stage 1 - Basic'
    STAGE_2 = '2', 'Stage 2 - Standard'
    STAGE_3 = '3', 'Stage 3 - Premium'
    STAGE_4 = '4', 'Stage 4 - Ultimate'


class SellerSubscription(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name='subscription')
    stage = models.CharField(max_length=5, choices=SubscriptionStage.choices, default=SubscriptionStage.STAGE_1)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.seller.business_name} - {self.get_stage_display()}"
