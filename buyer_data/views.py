from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
import buyer_data.models as models
import buyer_data.serializer as serializer
from rest_framework.response import Response

# Create your views here.
@api_view(['GET', 'HEAD'])
def view_buyer_model(r): return Response(serializer.BuyerSerializer(models.Buyer.objects.all(), many=True).data)

@api_view(['GET'])
def buyer_data(r, buyer_email): return Response(serializer.BuyerSerializer(get_object_or_404(models.Buyer, email=buyer_email, is_deleted=False)).data)
