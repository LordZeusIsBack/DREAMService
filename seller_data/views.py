from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from seller_data.models import Seller
from seller_data.serializer import SellerSerializer
from common.views import create_user_views
from common.models import CustomUser

# Create your views here.
seller_views = create_user_views(CustomUser, SellerSerializer, 'seller')

delete_seller = seller_views['delete_user']
update_seller_data = seller_views['update_user']
add_seller = seller_views['add_user']
seller_forgot_password = seller_views['forgot_password']
seller_reset_password = seller_views['reset_password']
seller_login = seller_views['login']

@api_view(['GET'])
def seller_data(r, seller_username): """
Retrieves and returns serialized data for a seller by username.

Args:
    seller_username: The username of the seller's associated user account.

Returns:
    A Response containing the serialized seller data if found; otherwise, returns a 404 error.
"""
return Response(SellerSerializer(get_object_or_404(Seller, user__username=seller_username, is_deleted=False)).data)
