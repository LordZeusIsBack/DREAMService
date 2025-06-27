from django.contrib import admin
from django.utils.html import format_html
from .models import Buyer, BuyerVerification, PurchasedEstate

# Register your models here.
@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    readonly_fields = ('phone_number',)
    list_display = ('user_email', 'first_name', 'last_name', 'username', 'phone_number')
    search_fields = ('user__email', 'phone_number', 'user__username')

    @admin.display(description='Email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='First Name')
    def first_name(self, obj):
        return obj.user.first_name

    @admin.display(description='Last Name')
    def last_name(self, obj):
        return obj.user.last_name

    @admin.display(description='Username')
    def username(self, obj):
        return obj.user.username

@admin.register(BuyerVerification)
class BuyerVerificationAdmin(admin.ModelAdmin):
    readonly_fields = ('aadhaar_number', 'pan_number')
    list_display = ('buyer_username', 'aadhaar_number', 'aadhaar_preview', 'pan_number', 'pan_preview')
    search_fields = ('aadhaar_number', 'pan_number')

    @admin.display(description='Buyer Username')
    def buyer_username(self, obj):
        return obj.buyer.user.username

    @admin.display(description='Aadhaar Card Preview')
    def aadhaar_preview(self, obj):
        if obj.aadhaar_card: return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.aadhaar_card.url)
        return "No Image"

    @admin.display(description='PAN Card Preview')
    def pan_preview(self, obj):
        if obj.pan_card: return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.pan_card.url)
        return "No Image"

@admin.register(PurchasedEstate)
class BuyerPurchaseAdmin(admin.ModelAdmin):
    readonly_fields = ('purchase_date', 'transaction_id')
    list_display = ('buyer', 'estate', 'purchase_date', 'transaction_id')
    search_fields = ('buyer__user__email', 'estate__estate_name', 'transaction_id')
