from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import buyer_data.models as buyer_models
from buyer_data.serializer import BuyerSerializer, PurchasedEstateSerializer
from rest_framework.response import Response
from common.views import create_user_views
from common.models import CustomUser

# Create your views here.
buyer_views = create_user_views(CustomUser, BuyerSerializer, 'buyer')

delete_buyer = buyer_views['delete_user']
update_buyer_data = buyer_views['update_user']
add_buyer = buyer_views['add_user']
buyer_forgot_password = buyer_views['forgot_password']
buyer_reset_password = buyer_views['reset_password']
buyer_login = buyer_views['login']

@api_view(['GET'])
def buyer_data(r, buyer_username): 
    """
    Retrieves and returns serialized data for a non-deleted buyer by username.

    Args:
        buyer_username: The username of the buyer to retrieve.

    Returns:
        A Response containing the serialized buyer data, or a 404 error if not found.
    """
    return Response(BuyerSerializer(get_object_or_404(buyer_models.Buyer, user__username=buyer_username, is_deleted=False)).data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_bought_estate(r):
    """
    Handles retrieval and creation of purchased estate records for the authenticated buyer.
    
    On GET, returns a list of estates purchased by the authenticated buyer. On POST, attempts to create a new purchased estate record for the buyer using the provided data. Returns validation errors if the input is invalid, or a server error message if an exception occurs during creation.
    """
    buyer = get_object_or_404(buyer_models.Buyer, user__username=r.user.username, is_deleted=False)
    if r.method == 'GET': return Response(PurchasedEstateSerializer(buyer_models.PurchasedEstate.objects.filter(buyer=buyer).select_related('estate'), many=True).data, status=status.HTTP_200_OK)
    elif r.method == 'POST':
        try:
            with transaction.atomic():
                serializer = PurchasedEstateSerializer(data=r.data, context={'request': r})
                if serializer.is_valid(): return Response(PurchasedEstateSerializer(serializer.save()).data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: return Response({'detail': 'Purchase failed due to server error. Please try again.', 'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
