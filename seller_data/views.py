from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from seller_data.models import Seller
from seller_data.serializer import SellerSerializer
from common.views import create_user_views
from common.models import CustomUser
import logging

logger = logging.getLogger('seller_data')

# Create your views here.
seller_views = create_user_views(CustomUser, SellerSerializer, 'seller')

delete_seller = seller_views['delete_user']
update_seller_data = seller_views['update_user']
add_seller = seller_views['add_user']
seller_forgot_password = seller_views['forgot_password']
seller_reset_password = seller_views['reset_password']
seller_login = seller_views['login']
seller_logout = seller_views['logout']
seller_verify_email = seller_views['verify']
seller_resend_otp = seller_views['resend_otp']

@api_view(['GET'])
def seller_data(r, seller_username):
    """
    Retrieve serialized seller information for a seller identified by username.
    
    Returns:
        Response: Serialized seller data if the seller exists; otherwise, returns a 404 error response.
    """
    return Response(SellerSerializer(get_object_or_404(Seller, user__username=seller_username)).data, status=HTTP_200_OK)

@api_view(['GET'])
def get_listed_estates(r, seller_username):
    """
    Retrieve all estates associated with a seller by username.
    
    If the seller has no estates, returns a 204 No Content response with a message. Otherwise, returns a list of serialized estate data with a 200 OK status.
    """
    from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
    from estate_data.models import Estate
    from estate_data.serializer import EstateSerializer
    estates = Estate.objects.filter(seller__user__username=seller_username).select_related('seller__user').prefetch_related('images')
    if not estates.exists(): return Response({'message': 'No estate available for selected seller'}, status=HTTP_204_NO_CONTENT)
    return Response(EstateSerializer(estates, many=True).data, status=HTTP_200_OK)
