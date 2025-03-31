from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import SellerSerializer
import api.models as models

# Create your views here.
@api_view(['GET'])
def index(r):
    return Response({'message': 'Hello, World!'})

@api_view(['GET', 'POST'])
def seller_models(r):
    if r.method == 'GET':
        return Response(SellerSerializer(models.Seller.objects.all(), many=True).data)
    else:
        serializer = SellerSerializer(data=r.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
