from rest_framework.response import Response
from rest_framework.decorators import api_view
import seller_data.serializer as serializer
import seller_data.models as models
import rest_framework.status as status
from django.shortcuts import get_object_or_404
from common.views import process_serializer

# Create your views here.
@api_view(['GET'])
def seller_data(r, seller_email): return Response(serializer.SellerSerializer(get_object_or_404(models.Seller, email=seller_email, is_deleted=False)).data)

@api_view(['PUT', 'PATCH'])
def update_seller_data(r, seller_email):
    seller = get_object_or_404(models.Seller, email=seller_email, is_deleted=False)
    data, resp_status = process_serializer(serializer.SellerSerializer, r.data, instance=seller)
    return Response(data, status=resp_status)

@api_view(['POST'])
def add_seller(r):
    data, resp_status = process_serializer(serializer.SellerSerializer, data=r.data)
    return Response(data, status=resp_status)

@api_view(['DELETE'])
def delete_seller(r, seller_email):
    obj = get_object_or_404(models.Seller, email=seller_email, is_deleted=False)
    obj.is_deleted = True
    obj.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
