from rest_framework.response import Response
from rest_framework.decorators import api_view
import api.serializer as serializer
import api.models as models
from rest_framework import status
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def seller_model_data(r, seller_id):
    seller = get_object_or_404(models.Seller, id=seller_id)
    serial = serializer.SellerSerializer(seller)
    return Response(serial.data)