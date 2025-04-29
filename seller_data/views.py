from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
import seller_data.models as models
import seller_data.serializer as seller_serializer
import common.serializer as common_serializer
import common.views as common_views

# Create your views here.
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

@api_view(['DELETE'])
def delete_seller(r, seller_username): return common_views.soft_delete_user(models.Seller, seller_username)

@api_view(['POST'])
@permission_classes([AllowAny])
def seller_forgot_password(r): return common_views.handle_password_reset(r.data, models.Seller, settings.FRONTEND_URL, common_serializer.PasswordResetRequestSerializer)

@api_view(['POST'])
@permission_classes([AllowAny])
def seller_reset_password(r): return common_views.handle_password_reset_conformation(r.data, models.Seller, common_serializer.PasswordResetConfirmSerializer)

@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def seller_login(r): return common_views.handle_user_login(r.data, models.Seller, seller_serializer.SellerSerializer, 'seller')
