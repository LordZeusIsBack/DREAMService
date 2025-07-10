from rest_framework import serializers
import seller_data.models as models
from common.serializer import BaseUserSerializer


class SellerVerificationSerializer(serializers.ModelSerializer):
    gstin = serializers.IntegerField()
    aadhaar_number = serializers.IntegerField()
    pan_number = serializers.CharField()
    class Meta:
        model = models.SellerVerification
        fields = ('gstin', 'aadhaar_number', 'pan_number')


class SellerSerializer(BaseUserSerializer):
    """
    Serializer for seller model.
    """
    aadhaar_number = serializers.IntegerField(write_only=True)
    pan_number = serializers.CharField(write_only=True)
    aadhaar_card = serializers.ImageField(required=False, write_only=True)
    pan_card = serializers.ImageField(required=False, write_only=True)
    gstin = serializers.IntegerField(write_only=True)
    agent_rera_id = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(required=False)
    business_name = serializers.CharField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')

    class Meta(BaseUserSerializer.Meta):
        model = models.Seller
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'business_name', 'username', 'password',
                  'aadhaar_number', 'pan_number', 'aadhaar_card', 'pan_card', 'gstin', 'agent_rera_id', 'profile_picture')

    def create(self, validated_data):
        verification_data = {
            'aadhaar_number': validated_data.pop('aadhaar_number'),
            'pan_number': validated_data.pop('pan_number'),
            'aadhaar_card': validated_data.pop('aadhaar_card', None),
            'pan_card': validated_data.pop('pan_card', None),
            'gstin': validated_data.pop('gstin'),
            'agent_rera_id': validated_data.pop('agent_rera_id')
        }
        validated_data['sellerverification'] = verification_data
        return BaseUserSerializer.create_user(
            validated_data,
            models.Seller,
            models.SellerVerification,
            'sellerverification'
        )

    def update(self, instance, validated_data):
        """
        Update an existing seller instance.
        """
        if 'business_name' in validated_data and validated_data['business_name'] != instance.business_name: raise serializers.ValidationError({'business_name': 'Cannot modify business_name once set.'})
        return BaseUserSerializer.update_user(
            instance,
            validated_data,
            'sellerverification'
        )
