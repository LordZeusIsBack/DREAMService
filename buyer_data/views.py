from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from buyer_data.models import Buyer
from buyer_data.serializer import BuyerSerializer
from rest_framework.response import Response
from common.views import create_user_views
from common.models import CustomUser

# Create your views here.
buyer_views = create_user_views(CustomUser, BuyerSerializer, 'buyer')

delete_buyer = buyer_views['delete_user']
update_buyer_data = buyer_views['update_user']
add_buyer = buyer_views['add_user']
buyer_forgot_password = buyer_views['forgot_password']
buyer_reset_password = buyer_views['reset_password']
buyer_login = buyer_views['login']
buyer_verify_email = buyer_views['verify']
buyer_resend_otp = buyer_views['resend_otp']

@api_view(['GET'])
def buyer_data(r, buyer_username): 
    """
    Retrieve and return serialized data for a buyer with the given username, excluding deleted buyers.
    
    Parameters:
        buyer_username (str): Username of the buyer to retrieve.
    
    Returns:
        Response: Serialized buyer data if found; otherwise, returns a 404 error response.
    """
    return Response(BuyerSerializer(get_object_or_404(Buyer, user__username=buyer_username)).data)
