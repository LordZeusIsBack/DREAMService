from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import SellerSerializer
import api.models as models
from rest_framework import status
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def seller_model_data(r):
    if r.method == 'GET':
        return Response(SellerSerializer(models.Seller.objects.all(), many=True).data)

@api_view(['PUT', 'PATCH'])
def seller_model_update(r):
    try:
        seller_id = r.data['id']
    except KeyError:
        return Response({'status': 'error', 'data': 'Seller ID not provided'},
                        status=status.HTTP_400_BAD_REQUEST)
    seller_obj = get_object_or_404(models.Seller, id=seller_id)
    partial_update = r.method == 'PATCH'
    serializer = SellerSerializer(seller_obj, data=r.data, partial=partial_update)
    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'success', 'data': serializer.data},
                        status=status.HTTP_200_OK)
    return Response({'status': 'error', 'data': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
