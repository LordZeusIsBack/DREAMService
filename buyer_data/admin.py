from django.contrib import admin
from .models import *

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

@admin.register(PurchasedEstate)
class BuyerPurchaseAdmin(admin.ModelAdmin):
    readonly_fields = ('purchase_date', 'transaction_id')
    list_display = ('buyer', 'estate', 'purchase_date', 'transaction_id')
    search_fields = ('buyer__user__email', 'estate__estate_name', 'transaction_id')
