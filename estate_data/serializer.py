from rest_framework import serializers
import estate_data.models as models


class EstateImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    class Meta:
        model = models.EstateImage
        fields = ['image']


class EstateSerializer(serializers.ModelSerializer):
    images = EstateImageSerializer(many=True, read_only=True)
    class Meta:
        model = models.Estate
        fields = ['seller', 'estate_name', 'estate_type', 'estate_price', 'status', 'location', 'images']

    def create(self, validated_data):
        estate = models.Estate.objects.create(**validated_data)
        request = self.context.get('request')
        if request and request.FILES:
            image_files = request.FILES.getlist('images')
            for image_file in image_files: models.EstateImage.objects.create(estate=estate, image=image_file)
        return estate
