from math import radians, sin, cos, asin, sqrt
import estate_data.models as models
from estate_data.serializer import EstateSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
import rest_framework.status as status

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    return (2 * asin(sqrt(a))) * 6371

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

@api_view(['GET'])
def area_estate(r):
    """
    Get all estates in a given area.
    """
    long = r.query_params.get('long')
    lat = r.query_params.get('lat')
    estate_type = r.query_params.get('estate_type')
    radius = float(r.query_params.get('radius', 10))
    if not long or not lat or not estate_type: return Response({"error": "Missing required query parameters: long, lat or estate_type."}, status=status.HTTP_400_BAD_REQUEST)
    estates = models.Estate.objects.filter(estate_type=estate_type, status='available')
    result = []
    for estate in estates:
        if estate.latitude and estate.longitude:
            distance = haversine(long, lat, estate.longitude, estate.latitude)
            if distance <= radius:
                estate.distance = distance
                result.append(estate)
    data = EstateSerializer(result, many=True).data

    for i, estate in enumerate(result): data[i]['distance'] = estate.distance

    return Response(data, status=status.HTTP_200_OK)
