from rest_framework import serializers
import estate_data.models as estate_models
from common.serializer import BaseUserSerializer
import buyer_data.models as models


class BuyerSerializer(BaseUserSerializer):
    """
    Serializer for buyer model.
    """
    aadhaar_number = serializers.IntegerField(required=False, write_only=True)
    pan_number = serializers.CharField(required=False, write_only=True)
    aadhaar_card = serializers.ImageField(required=False, write_only=True)
    pan_card = serializers.ImageField(required=False, write_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email', required=False)
    username = serializers.CharField(source='user.username', required=False)
    profile_picture = serializers.ImageField(required=False)
    class Meta(BaseUserSerializer.Meta):
        model = models.Buyer
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'password', 'aadhaar_number',
                  'pan_number', 'aadhaar_card', 'pan_card', 'profile_picture')

    def __init__(self, *args, **kwargs):
        """
        Initializes the serializer and sets specific fields as required when creating a new buyer.
        
        Fields 'aadhaar_number', 'pan_number', 'email_number', and 'username_number' are marked as required only if the serializer is used for creation (i.e., no existing instance is provided).
        """
        super(BuyerSerializer, self).__init__(*args, **kwargs)
        if self.instance is None:
            self.fields['aadhaar_number'].required = True
            self.fields['pan_number'].required = True
            self.fields['phone_number'].required = True
            self.fields['email'].required = True
            self.fields['username'].required = True

    def create(self, validated_data):
        """
        Create a new buyer and associated verification record using the provided validated data.
        
        Parameters:
            validated_data (dict): Data containing buyer and verification fields.
        
        Returns:
            Buyer: The newly created buyer instance with linked verification details.
        """
        verification_data = {
            'aadhaar_number': validated_data.pop('aadhaar_number'),
            'pan_number': validated_data.pop('pan_number'),
            'aadhaar_card': validated_data.pop('aadhaar_card', None),
            'pan_card': validated_data.pop('pan_card', None),
        }
        validated_data['buyerverification'] = verification_data
        return BaseUserSerializer.create_user(
            validated_data,
            models.Buyer,
            models.BuyerVerification,
            'buyerverification'
        )

    def validate(self, attrs):
        """
        Validates that `aadhaar_number` and `pan_number` are provided when creating a new buyer.
        
        Raises a validation error if either field is missing during creation. No validation is performed for these fields during updates.
        
        Parameters:
            attrs (dict): The input data to validate.
        
        Returns:
            dict: The validated attributes.
        """
        if self.instance is None:
            if not attrs.get('aadhaar_number'): raise serializers.ValidationError({'aadhaar_number': 'This field is required during creation.'})
            if not attrs.get('pan_number'): raise serializers.ValidationError({'pan_number': 'This field is required during creation.'})
        return attrs

    def update(self, instance, validated_data):
        """
        Update a buyer instance along with its associated verification details.
        
        Delegates the update process to the base user serializer to ensure both buyer and verification information are updated together.
        
        Returns:
            The updated buyer instance.
        """
        return BaseUserSerializer.update_user(
            instance,
            validated_data,
            'buyerverification'
        )


class EstateImagesSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = estate_models.EstateImage
        fields = ('image_url',)


class EstateDataSerializer(serializers.ModelSerializer):
    images = EstateImagesSerializer(many=True, read_only=True)
    class Meta:
        model = estate_models.Estate
        fields = ('id', 'estate_name', 'estate_price', 'slug', 'images')


class WishlistItemSerializer(serializers.ModelSerializer):
    estate = EstateDataSerializer()

    class Meta:
        model = models.WishlistItem
        fields = ['estate', 'added_on']
