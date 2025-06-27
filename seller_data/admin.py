from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    readonly_fields = ('business_name', 'phone_number')
    list_display = ('seller_username', 'seller_email', 'business_name', 'phone_number')

    @admin.display(description='Seller Email')
    def seller_email(self, obj):
        """
        Returns the email address of the user associated with the given seller object.
        
        Parameters:
            obj: The seller instance for which to retrieve the user's email.
        
        Returns:
            str: The email address of the associated user.
        """
        return obj.user.email

    @admin.display(description='Seller Username')
    def seller_username(self, obj):
        """
        Returns the username of the user associated with the seller for display in the admin interface.
        """
        return obj.seller.user.username

@admin.register(SellerVerification)
class SellerVerificationAdmin(admin.ModelAdmin):
    readonly_fields = ('aadhaar_number', 'pan_number', 'agent_rera_id', 'gstin')
    list_display = ('seller_username', 'aadhaar_number', 'pan_number', 'agent_rera_id', 'gstin')
    search_fields = ('seller__user__username', 'aadhaar_number', 'pan_number', 'agent_rera_id', 'gstin')

    @admin.display(description='Seller Username')
    def seller_username(self, obj):
        """
        Returns the username of the user associated with the seller for display in the admin interface.
        """
        return obj.seller.user.username
