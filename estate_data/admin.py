from django.contrib import admin
from .models import EstateImage, Estate
from django.utils.html import format_html

# Register your models here.
@admin.register(EstateImage)
class EstateImageAdmin(admin.ModelAdmin):
    list_display = ['estate', 'image_preview']

    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        """
        Return an HTML image preview for an EstateImage object in the Django admin list view.
        
        If the object has an associated image, displays a scaled image preview; otherwise, returns "No Image".
        """
        if obj.image: return format_html('<img src="{}" width="100" style="object-fit:contain;" />', obj.image.url)
        return "No Image"

@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ['seller_username', 'estate_name', 'estate_type', 'estate_price', 'status', 'latitude', 'longitude', 'created_at', 'updated_at']
    search_fields = ['seller__user__username', 'estate_type', 'estate_price']

    @admin.display(description='Seller Username')
    def seller_username(self, obj):
        """
        Returns the username of the seller associated with the given estate object.
        
        Parameters:
            obj: The estate instance for which to retrieve the seller's username.
        
        Returns:
            str: The username of the seller linked to the estate.
        """
        return obj.seller.user.username
