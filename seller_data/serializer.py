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
    verification = SellerVerificationSerializer(source='sellerverification', read_only=False)
    business_name = serializers.CharField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')

    class Meta(BaseUserSerializer.Meta):
        model = models.Seller
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'business_name', 'username', 'password',
                  'verification')

    def create(self, validated_data):
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
        return BaseUserSerializer.update_user(
            instance,
            validated_data,
            'sellerverification'
        )
