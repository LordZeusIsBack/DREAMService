from rest_framework.response import Response
from rest_framework.decorators import api_view
import seller_data.serializer as serializer
import seller_data.models as models

# Create your views here.
@api_view(['GET'])
def model_data(r): return Response(serializer.SellerSerializer(models.Seller.objects.all(), many=True).data)
