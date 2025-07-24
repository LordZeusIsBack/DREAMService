from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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
        fields = ['seller', 'estate_name', 'estate_type', 'estate_government_id', 'estate_price', 'status',
                  'slug', 'description', 'latitude', 'longitude', 'images', 'images_to_delete']

    def create(self, validated_data):
        """
        Create a new Estate instance with the given validated data and associate any uploaded images from the request.
        
        Removes the 'images_to_delete' field from the input data if present. For each image file uploaded under the 'images' key in the request, creates an EstateImage linked to the new estate.
        
        Returns:
            Estate: The newly created Estate instance.
        """
        if 'images_to_delete' in validated_data: validated_data.pop('images_to_delete')
        estate = models.Estate.objects.create(**validated_data)
        request = self.context.get('request')
        if request and request.FILES:
            image_files = request.FILES.getlist('images')
            for image_file in image_files: models.EstateImage.objects.create(estate=estate, image=image_file)
        return estate

    def validate(self, attrs):
        """
        Ensures that the estate's government ID cannot be changed after creation.
        
        Raises a ValidationError if an update attempt modifies the existing estate_government_id.
        """
        if self.instance and 'estate_government_id' in attrs:
            if attrs['estate_government_id'] != self.instance.estate_government_id: raise ValidationError('Government ID cannot be changed once set!')
        return attrs

    def update(self, instance, validated_data):
        """
        Updates an existing estate instance with new data and manages associated images.
        
        If a list of image IDs to delete is provided, removes those images from the estate. Adds any new uploaded images to the estate. Returns the updated estate instance.
        """
        images_to_delete = validated_data.pop('images_to_delete', None)
        if images_to_delete:
            images_to_remove = models.EstateImage.objects.filter(id__in=images_to_delete, estate=instance)
            for img in images_to_remove:
                storage = img.image.storage
                if storage.exists(img.image.name): storage.delete(img.image.name)
            images_to_remove.delete()
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        instance.save()
        request = self.context.get('request')
        if request and request.FILES:
            image_files = request.FILES.getlist('images')
            for image_file in image_files: models.EstateImage.objects.create(estate=instance, image=image_file)
        return instance


class EstateListSerializer(serializers.ModelSerializer):
    images = EstateImageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Estate
        fields = ['slug', 'estate_name', 'estate_price', 'estate_type', 'images']
