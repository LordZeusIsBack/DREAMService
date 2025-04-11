from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
import buyer_data.models as models
import buyer_data.serializer as serializer
from rest_framework.response import Response
from common.views import process_serializer

# Create your views here.
@api_view(['GET', 'HEAD'])
def view_buyer_model(r): return Response(serializer.BuyerSerializer(models.Buyer.objects.all(), many=True).data)

@api_view(['GET'])
def buyer_data(r, buyer_username): return Response(serializer.BuyerSerializer(get_object_or_404(models.Buyer, username=buyer_username, is_deleted=False)).data)

@api_view(['PUT', 'PATCH'])
def update_buyer_data(r, seller_username):
    seller = get_object_or_404(models.Buyer, username=seller_username, is_deleted=False)
    data, resp_status = process_serializer(serializer.BuyerSerializer, r.data, instance=seller)
    return Response(data, status=resp_status)
