from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import buyer_data.models as models
import buyer_data.serializer as buyer_serializer
from rest_framework.response import Response
import common.views as common_views
import common.serializer as common_serializer
from django.conf import settings

# Create your views here.
@api_view(['GET'])
def buyer_data(r, buyer_username): return Response(buyer_serializer.BuyerSerializer(get_object_or_404(models.Buyer, username=buyer_username, is_deleted=False)).data)

@api_view(['PUT', 'PATCH'])
def update_buyer_data(r, buyer_username):
    obj = get_object_or_404(models.Buyer, username=buyer_username, is_deleted=False)
    data, resp_status = common_views.process_serializer(buyer_serializer.BuyerSerializer, r.data, instance=obj)
    return Response(data, status=resp_status)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_buyer(r):
    data, resp_status = common_views.process_serializer(buyer_serializer.BuyerSerializer, data=r.data)
    return Response(data, status=resp_status)
