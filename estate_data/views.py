import models
from serializer import EstateSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
import rest_framework.status as status

# Create your views here.
@api_view(['GET'])
def get_estate_data(r, estate_slug): return Response(EstateSerializer(get_object_or_404(models.Estate, slug=estate_slug)).data)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_new_estate(r):
    """
    Add new estate data.
    """
    serializer = EstateSerializer(data=r.data, context={'request': r})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@parser_classes([MultiPartParser, FormParser])
def update_estate_data(r, slug):
    """
    Update estate data.
    """
    with transaction.atomic():
        estate = get_object_or_404(models.Estate, slug=slug)
        serializer = EstateSerializer(estate, data=r.data, context={'request': r}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
