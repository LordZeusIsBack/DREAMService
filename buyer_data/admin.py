from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(PurchasedEstate)
class BuyerPurchaseAdmin(admin.ModelAdmin):
    readonly_fields = ('purchase_date', 'transaction_id')
    list_display = ('buyer', 'estate', 'purchase_date', 'transaction_id')
    search_fields = ('buyer__user__email', 'estate__estate_name', 'transaction_id')
