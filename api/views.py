from rest_framework.response import Response
from rest_framework.decorators import api_view
import api.serializer as serializer
import api.models as models
from rest_framework import status
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def seller_model_data(r, seller_id): return Response(serializer.SellerSerializer(get_object_or_404(models.Seller, id=seller_id)).data)

@api_view(['PUT'])
def update_seller_model_data(request, seller_id):
    seller = get_object_or_404(models.Seller, id=seller_id)
    serializer_instance = serializer.SellerSerializer(seller, data=request.data, partial=True)
    if serializer_instance.is_valid():
        try:
            serializer_instance.save()
            return Response(serializer_instance.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
