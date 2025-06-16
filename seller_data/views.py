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
def seller_data(r, seller_username):
    """
    Retrieves seller data for a given username.

    Returns serialized seller information if the seller exists and is not marked as deleted; otherwise, returns a 404 error.
    """
    return Response(SellerSerializer(get_object_or_404(Seller, user__username=seller_username, is_deleted=False)).data)

@api_view(['GET'])
def get_listed_estates(r, seller_username):
    """
    Retrieves a list of estates associated with a given seller username.
    
    Returns a 204 No Content response with a message if the seller has no estates. Otherwise, returns serialized estate data for the seller with a 200 OK status.
    """
    from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
    from estate_data.models import Estate
    from estate_data.serializer import EstateSerializer
    estates = Estate.objects.filter(seller__user__username=seller_username, seller__is_deleted=False).select_related('seller__user').prefetch_related('images')
    if not estates.exists(): return Response({'message': 'No estate available for selected seller'}, status=HTTP_204_NO_CONTENT)
    return Response(EstateSerializer(estates, many=True).data, status=HTTP_200_OK)
