from rest_framework import serializers
import estate_data.models as models


class EstateImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    class Meta:
        model = models.EstateImage
        fields = ['image']


class EstateSerializer(serializers.ModelSerializer):
    images = EstateImageSerializer(many=True)
    class Meta:
        model = models.Estate
        fields = ['seller', 'estate_name', 'estate_type', 'estate_price', 'status', 'location', 'images']
