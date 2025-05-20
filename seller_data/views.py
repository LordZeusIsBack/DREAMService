from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from seller_data.models import Seller
from seller_data.serializer import SellerSerializer
import common.views as common_views
from common.models import CustomUser

# Create your views here.
seller_views = common_views.create_user_views(CustomUser, SellerSerializer, 'seller')

delete_seller = seller_views['delete_user']
seller_forgot_password = seller_views['forgot_password']
seller_reset_password = seller_views['reset_password']
seller_login = seller_views['login']

@api_view(['GET'])
def seller_data(r, seller_username): return Response(SellerSerializer(get_object_or_404(Seller, user__username=seller_username, is_deleted=False)).data)

@api_view(['PUT', 'PATCH'])
def update_seller_data(r, seller_username):
    seller = get_object_or_404(Seller, user__username=seller_username, is_deleted=False)
    data, resp_status = common_views.process_serializer(SellerSerializer, r.data, instance=seller)
    return Response(data, status=resp_status)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_seller(r):
    data, resp_status = common_views.process_serializer(SellerSerializer, data=r.data)
    return Response(data, status=resp_status)
