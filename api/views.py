from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import SellerSerializer
import api.models as models


@api_view(['GET'])
def seller_model_data(r):
    if r.method == 'GET':
        return Response(SellerSerializer(models.Seller.objects.all(), many=True).data)