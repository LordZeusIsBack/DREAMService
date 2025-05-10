from uuid import uuid4
from django.db import models
from seller_data.models import Seller
from django.utils.text import slugify

def estate_image_path(instance, filename): return f'picture/estate_images/{instance.estate.slug}/{filename}'

# Create your models here.
class Estate(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
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
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"{self.estate_name} - {self.estate_type}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.estate_name)
            candidate = f"{base_slug}-{uuid4().hex[:8]}"
            while Estate.objects.filter(slug=candidate).exists(): candidate = f"{base_slug}-{uuid4().hex[:8]}"
            self.slug = base_slug
        return super().save(*args, **kwargs)

class EstateImage(models.Model):
    estate = models.ForeignKey(Estate, related_name='images', on_delete=models.CASCADE, related_query_name='image')
    image = models.ImageField(upload_to=estate_image_path)

    def __str__(self): return f"Image for {self.estate.estate_name}"
