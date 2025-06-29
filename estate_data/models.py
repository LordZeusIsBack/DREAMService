from uuid import uuid4
from django.db import models
from rest_framework.exceptions import ValidationError
from seller_data.models import Seller
from django.utils.text import slugify
from common.utils.storage_backends import MediaStorage

def estate_image_path(instance, filename):
    """
    Generate a unique and safe file path for uploading an estate image.
    
    The path includes a slugified version of the estate's name, a short UUID segment for uniqueness, and preserves the original file extension. The resulting path format is: 'estate_images/{estate_slug}/images/{safe_filename}'.
    
    Parameters:
        instance: The EstateImage instance containing the related estate.
        filename: The original name of the uploaded file.
    
    Returns:
        str: The generated file path for storing the image.
    """
    base, extension = filename.rsplit('.', 1)
    safe_filename = f'{slugify(instance.estate.estate_name)}-{uuid4().hex[:8]}.{extension}'
    return f'estate_images/{instance.estate.slug}/images/{safe_filename}'

# Create your models here.
class Estate(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    estate_government_id = models.CharField(max_length=255, unique=True, db_index=True)
    estate_name = models.CharField(max_length=255)
    estate_type = models.CharField(max_length=255, choices=[
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
        ('villa', 'Villa'),
        ('townhouse', 'Townhouse'),
        ('duplex', 'Duplex'),
        ('studio', 'Studio'),
        ('penthouse', 'Penthouse'),
        ('cottage', 'Cottage')
    ])
    estate_price = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(max_length=255, choices=[
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
        ('pending', 'Pending')
    ])
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, db_index=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"{self.estate_name} - {self.estate_type}"

    def save(self, *args, **kwargs):
        """
        Saves the Estate instance, generating a unique slug if one is not set.
        
        If the slug field is empty, a unique slug is created from the estate name and a random UUID segment, ensuring no conflicts with existing slugs before saving.
        """
        if not self.slug:
            base_slug = slugify(self.estate_name)
            candidate = f"{base_slug}-{uuid4().hex[:8]}"
            while Estate.objects.filter(slug=candidate).exists(): candidate = f"{base_slug}-{uuid4().hex[:8]}"
            self.slug = candidate
        if self.pk:
            original = Estate.objects.get(pk=self.pk)
            if original.estate_government_id != self.estate_government_id: raise ValidationError('Government ID cannot be changed once set!')
        return super().save(*args, **kwargs)

class EstateImage(models.Model):
    estate = models.ForeignKey(Estate, related_name='images', on_delete=models.CASCADE, related_query_name='image')
    image = models.ImageField(upload_to=estate_image_path, storage=MediaStorage)

    def __str__(self):
        """
        Return a string representation indicating the image is associated with a specific estate.
        """
        return f"Image for {self.estate.estate_name}"
