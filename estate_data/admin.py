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
        Return an HTML image preview for the estate image in the Django admin list view.
        
        If the estate image exists, displays a scaled image; otherwise, returns "No Image".
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
        Return the username of the user associated with the estate's seller.
        
        Parameters:
            obj: The Estate instance for which to retrieve the seller's username.
        
        Returns:
            str: The username of the seller's user account.
        """
        return obj.seller.user.username
