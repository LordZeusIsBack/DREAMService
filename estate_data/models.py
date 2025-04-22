from django.db import models
from django.contrib.gis.db import models as gis_models
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
    location = gis_models.PointField(geography=True)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"{self.estate_name} - {self.estate_type}"

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.estate_name)
        return super().save(*args ,**kwargs)


class EstateImage(models.Model):
    estate = models.ForeignKey(Estate, related_name='images', on_delete=models.CASCADE, related_query_name='image')
    image = models.ImageField(upload_to=estate_image_path)

    def __str__(self): return f"Image for {self.estate.estate_name}"
