from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    readonly_fields = ('phone_number',)
    list_display = ('user', 'user__first_name', 'user__last_name', 'phone_number')
    search_fields = ('user__username', 'phone_number')

@admin.register(PurchasedEstate)
class BuyerPurchaseAdmin(admin.ModelAdmin):
    readonly_fields = ('purchase_date', 'transaction_id')
    list_display = ('buyer', 'estate', 'purchase_date', 'transaction_id')
    search_fields = ('buyer__user__email', 'estate__estate_name', 'transaction_id')
