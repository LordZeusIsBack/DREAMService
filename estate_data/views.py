from math import radians, degrees, sin, cos, asin, sqrt
import requests
import estate_data.models as models
from estate_data.serializer import EstateSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
import rest_framework.status as status
from django.conf import settings

def bounding_box(lat, long, radius):
    lat, long, earth_radius = float(lat), float(long), 6371
    delta_lat, delta_long = degrees(radius / earth_radius), degrees(radius / (earth_radius * cos(radians(lat))))
    return (
        lat - delta_lat,
        lat + delta_lat,
        long - delta_long,
        long + delta_long
    )

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
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
    serializer = EstateSerializer(data=r.data, context={'request': r})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@parser_classes([MultiPartParser, FormParser])
def update_estate_data(r, slug):
    with transaction.atomic():
        estate = get_object_or_404(models.Estate, slug=slug)
        serializer = EstateSerializer(estate, data=r.data, context={'request': r}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def area_estate(request):
    place = request.query_params.get('place')
    lat = request.query_params.get('lat')
    long = request.query_params.get('long')
    estate_type = request.query_params.get('estate_type')
    radius = float(request.query_params.get('radius', 10))

    # Resolve lat/long from place if place is provided and lat/long are missing
    if place and (not lat or not long):
        geo_url = f"https://api.geoapify.com/v1/geocode/search"
        params = {
            "text": place,
            "format": "json",
            "apiKey": settings.GEOAPIFY_API_KEY
        }
        try:
            geo_response = requests.get(geo_url, params=params)
            geo_data = geo_response.json()

            if not geo_data['results']:
                return Response({"error": f"Could not find location for place: {place}"}, status=status.HTTP_400_BAD_REQUEST)

            lat = geo_data['results'][0]['lat']
            long = geo_data['results'][0]['lon']
        except Exception as e:
            return Response({"error": "Failed to fetch coordinates from Geoapify.", "details": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    # Validate essential query params
    if not lat or not long or not estate_type:
        return Response({"error": "Missing required parameters: 'lat', 'long', or 'estate_type'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        lat = float(lat)
        long = float(long)
    except ValueError:
        return Response({"error": "Latitude and longitude must be valid float numbers."}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate bounding box
    min_lat, max_lat, min_long, max_long = bounding_box(lat, long, radius)

    # Filter estates within the bounding box and available
    estates = models.Estate.objects.filter(
        estate_type=estate_type,
        latitude__gte=min_lat,
        latitude__lte=max_lat,
        longitude__gte=min_long,
        longitude__lte=max_long,
        status='available'
    )

    # Apply precise Haversine filter
    result = [estate for estate in estates if haversine(lat, long, estate.latitude, estate.longitude) <= radius]

    # Serialize and return
    data = EstateSerializer(result, many=True).data
    return Response(data, status=status.HTTP_200_OK)