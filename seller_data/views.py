from rest_framework.response import Response
from rest_framework.decorators import api_view
import seller_data.serializer as serializer
import seller_data.models as models
import rest_framework.status as status
from django.shortcuts import get_object_or_404
from common.views import process_serializer

# Create your views here.
@api_view(['GET'])
def model_data(r): return Response(serializer.SellerSerializer(models.Seller.objects.filter(is_deleted=False), many=True).data)

@api_view(['GET'])
def seller_data(r, seller_id):
    obj = get_object_or_404(models.Seller, id=seller_id)
    serial_instance = serializer.SellerSerializer(obj)
    return Response(serial_instance.data)

@api_view(['PUT'])
def update_seller_data(r, seller_id):
    seller = get_object_or_404(models.Seller, id=seller_id)
    data, resp_status = process_serializer(serializer.SellerSerializer, r.data, instance=seller)
    return Response(data, status=resp_status)

@api_view(['POST'])
def add_seller(r):
    data, resp_status = process_serializer(serializer.SellerSerializer, data=r.data)
    return Response(data, status=resp_status)

@api_view(['DELETE'])
def delete_seller(r, seller_id):
    obj = get_object_or_404(models.Seller, id=seller_id)
    obj.is_deleted = True
    obj.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
