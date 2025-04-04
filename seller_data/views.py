from rest_framework.response import Response
from rest_framework.decorators import api_view
import seller_data.serializer as serializer
import seller_data.models as models
from django.shortcuts import get_object_or_404

# Create your views here.
@api_view(['GET'])
def model_data(r): return Response(serializer.SellerSerializer(models.Seller.objects.all(), many=True).data)

@api_view(['GET'])
def seller_data(r, seller_id):
    obj = get_object_or_404(models.Seller, id=seller_id)
    serial_instance = serializer.SellerSerializer(obj)
    return Response(serial_instance.data)
