from django.contrib import admin
from .models import EstateImage, Estate
from django.utils.html import format_html

# Register your models here.
@admin.register(EstateImage)
class EstateImageAdmin(admin.ModelAdmin):
    list_display = ['estate', 'image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="object-fit:contain;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Image Preview'

@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ['estate_name', 'estate_type', 'estate_price', 'status', 'latitude', 'longitude', 'slug', 'created_at', 'updated_at']
