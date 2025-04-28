from rest_framework import serializers
import estate_data.models as models


class EstateImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(required=True)
    class Meta:
        model = models.EstateImage
        fields = ['id', 'image']


class EstateSerializer(serializers.ModelSerializer):
    images = EstateImageSerializer(many=True, read_only=True)
    images_to_delete = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    class Meta:
        model = models.Estate
        fields = ['seller', 'estate_name', 'estate_type', 'estate_price', 'status', 'slug', 'location', 'images',
                  'images_to_delete']

    def create(self, validated_data):
        if 'images_to_delete' in validated_data: validated_data.pop('images_to_delete')
        estate = models.Estate.objects.create(**validated_data)
        request = self.context.get('request')
        if request and request.FILES:
            image_files = request.FILES.getlist('images')
            for image_file in image_files: models.EstateImage.objects.create(estate=estate, image=image_file)
        return estate

    def update(self, instance, validated_data):
        images_to_delete = validated_data.pop('images_to_delete', None)
        if images_to_delete: models.EstateImage.objects.filter(id__in=images_to_delete, estate=instance).delete()
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        instance.save()
        request = self.context.get('request')
        if request and request.FILES:
            image_files = request.FILES.getlist('images')
            for image_file in image_files: models.EstateImage.objects.create(estate=instance, image=image_file)
        return instance
