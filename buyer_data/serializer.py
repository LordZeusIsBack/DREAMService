from rest_framework import serializers
from common.serializer import BaseUserSerializer
import buyer_data.models as models


class BuyerVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for buyer verification.
    """
    aadhaar_number = serializers.IntegerField()
    pan_number = serializers.CharField()
    aadhaar_card = serializers.ImageField(required=False)
    pan_card = serializers.ImageField(required=False)
    class Meta:
        model = models.BuyerVerification
        fields = ('aadhaar_number', 'pan_number', 'aadhaar_card', 'pan_card')


class BuyerSerializer(BaseUserSerializer):
    """
    Serializer for buyer model.
    """
    aadhaar_number = serializers.IntegerField(write_only=True)
    pan_number = serializers.CharField(write_only=True)
    aadhaar_card = serializers.ImageField(required=False, write_only=True)
    pan_card = serializers.ImageField(required=False, write_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    profile_picture = serializers.ImageField(required=False)
    class Meta(BaseUserSerializer.Meta):
        model = models.Buyer
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'password', 'aadhaar_number',
                  'pan_number', 'aadhaar_card', 'pan_card', 'profile_picture')

    def create(self, validated_data):
        """
        Creates a new buyer along with associated verification data.
        
        Returns:
            Buyer: The newly created buyer instance.
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

    def update(self, instance, validated_data):
        """
        Update a buyer instance and its related verification details.
        
        Delegates the update process to the base user serializer, ensuring that both buyer and associated verification information are updated in a single operation.
        
        Returns:
            The updated buyer instance.
        """
        return BaseUserSerializer.update_user(
            instance,
            validated_data,
            'buyerverification'
        )
