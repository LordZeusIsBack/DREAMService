from geopy import Nominatim
import estate_data.models as models
from estate_data.serializer import EstateSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
import rest_framework.status as status
from rest_framework import generics
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.views.decorators.cache import cache_page
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

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

class EstateAreaView(generics.ListAPIView):
    """
    Returns all available estates of a given type within a core radius,
    plus those in the surrounding ring (core_radius < distance ≤ outer_radius),
    ordered by distance.
    Expected query params:
    - estate_type   (required)
    - area          (required): any string geocodable by Nominatim
    - core_radius   (optional, defaults to 5 km)
    - outer_radius  (optional, defaults to core_radius + 5 km)
    """
    serializer_class = EstateSerializer

    def get(self, request, *args, **kwargs):
        if 'estate_type' not in request.query_params or 'area' not in request.query_params: return Response({'error': 'Missing required query parameters: estate_type and area'}, status=status.HTTP_400_BAD_REQUEST)

    @cache_page(60 * 60)
    def get_queryset(self):
        estate_type = self.request.query_params.get('estate_type')
        area = self.request.query_params.get('area')
        core_radius = float(self.request.query_params.get('core_radius', 5))
        outer_radius = float(self.request.query_params.get('outer_radius', core_radius + 5))

        geolocator = Nominatim(user_agent='estate_data')
        try: location = geolocator.geocode(area)
        except (GeocoderTimedOut, GeocoderServiceError): return models.Estate.objects.none()

        if not location: return models.Estate.objects.none()

        center = Point(location.longitude, location.latitude, srid=4326)
        base_qs = (models.Estate.objects.filter(estate_type=estate_type, status='available').annotate(distance=Distance('location', center)))
        combined_qs = base_qs.filter(Q(distance__lte=D(km=core_radius)) | Q(distance__gt=D(km=core_radius), distance__lte=D(km=outer_radius))).order_by('distance')

        return combined_qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data)
