from rest_framework.response import Response
from rest_framework.decorators import api_view
import api.serializer as serializer
import api.models as models
from rest_framework import status
from django.shortcuts import get_object_or_404


def process_serializer(serializer_class, data, instance=None, success_status=status.HTTP_200_OK, create_status=status.HTTP_201_CREATED):
    serializer_instance = serializer_class(instance, data=data) if instance else serializer_class(data=data)
    if serializer_instance.is_valid():
        try:
            serializer_instance.save()
            return serializer_instance.data, (success_status if instance else create_status)
        except Exception as e:
            return {'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    return serializer_instance.errors, status.HTTP_400_BAD_REQUEST

@api_view(['GET'])
def model_data(r): return Response(serializer.SellerSerializer(models.Seller.objects.all(), many=True).data)

@api_view(['GET'])
def seller_model_data(r, seller_id): return Response(serializer.SellerSerializer(get_object_or_404(models.Seller, id=seller_id)).data)

@api_view(['PUT'])
def update_seller_model_data(request, seller_id):
    seller = get_object_or_404(models.Seller, id=seller_id)
    data, resp_status = process_serializer(serializer.SellerSerializer, instance=seller, data=request.data)
    return Response(data, status=resp_status)

@api_view(['POST'])
def add_new_user(request):
    data, resp_status = process_serializer(serializer.SellerSerializer, data=request.data)
    return Response(data, status=resp_status)
