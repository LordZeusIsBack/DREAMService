from django.contrib import admin
from .models import Seller, SellerVerification

# Register your models here.
@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    readonly_fields = ('business_name', 'phone_number')
    list_display = ('seller_username', 'seller_email', 'business_name', 'phone_number')

    @admin.display(description='Seller Email')
    def seller_email(self, obj):
        """
        Returns the email address of the user associated with the given Seller instance.
        
        Parameters:
            obj: The Seller model instance.
        
        Returns:
            str: The email address of the related user.
        """
        return obj.user.email

    @admin.display(description='Seller Username')
    def seller_username(self, obj):
        """
        Returns the username of the user associated with the seller for the given SellerVerification instance.
        
        Parameters:
            obj: The SellerVerification instance being displayed.
        
        Returns:
            str: The username of the related user.
        """
        return obj.seller.user.username

@admin.register(SellerVerification)
class SellerVerificationAdmin(admin.ModelAdmin):
    readonly_fields = ('pan_number', 'agent_rera_id', 'gstin')
    list_display = ('seller_username', 'pan_number', 'agent_rera_id', 'gstin')
    search_fields = ('seller__user__username', 'pan_number', 'agent_rera_id', 'gstin')

    @admin.display(description='Seller Username')
    def seller_username(self, obj):
        """
        Return the username of the user associated with the seller for the given SellerVerification instance.
        
        Parameters:
            obj: The SellerVerification instance for which to retrieve the seller's username.
        
        Returns:
            str: Username of the related user.
        """
        return obj.seller.user.username
