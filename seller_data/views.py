from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
import seller_data.models as models
import seller_data.serializer as seller_serializer
from common.views import create_user_views
import common.views as common_views

# Create your views here.
seller_views = create_user_views(models.Seller, seller_serializer.SellerSerializer, 'seller')

delete_seller = seller_views['delete_user']
seller_forgot_password = seller_views['forgot_password']
seller_reset_password = seller_views['reset_password']
seller_login = seller_views['login']

@api_view(['GET'])
def seller_data(r, seller_username): return Response(seller_serializer.SellerSerializer(get_object_or_404(models.Seller, username=seller_username, is_deleted=False)).data)

@api_view(['PUT', 'PATCH'])
def update_seller_data(r, seller_username):
    seller = get_object_or_404(models.Seller, username=seller_username, is_deleted=False)
    data, resp_status = common_views.process_serializer(seller_serializer.SellerSerializer, r.data, instance=seller)
    return Response(data, status=resp_status)

@api_view(['POST'])
def add_seller(r):
    data, resp_status = common_views.process_serializer(seller_serializer.SellerSerializer, data=r.data)
    return Response(data, status=resp_status)