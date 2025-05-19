from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from buyer_data.models import Buyer
from buyer_data.serializer import BuyerSerializer
from rest_framework.response import Response
import common.views as common_views

# Create your views here.
buyer_views = common_views.create_user_views(Buyer, BuyerSerializer, 'buyer')

delete_buyer = buyer_views['delete_user']
buyer_forgot_password = buyer_views['forgot_password']
buyer_reset_password = buyer_views['reset_password']
buyer_login = buyer_views['login']

@api_view(['GET'])
def buyer_data(r, buyer_username): return Response(BuyerSerializer(get_object_or_404(Buyer, user__username=buyer_username, is_deleted=False)).data)

@api_view(['PUT', 'PATCH'])
def update_buyer_data(r, buyer_username):
    obj = get_object_or_404(Buyer, user__username=buyer_username, is_deleted=False)
    data, resp_status = common_views.process_serializer(BuyerSerializer, r.data, instance=obj)
    return Response(data, status=resp_status)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_buyer(r):
    data, resp_status = common_views.process_serializer(BuyerSerializer, data=r.data)
    return Response(data, status=resp_status)
