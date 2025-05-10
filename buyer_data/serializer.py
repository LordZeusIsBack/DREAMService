from rest_framework import serializers
from common.serializer import BaseUserSerializer
import buyer_data.models as models


class BuyerVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for buyer verification.
    """
    aadhaar_number = serializers.IntegerField()
    pan_number = serializers.CharField()
    class Meta:
        model = models.BuyerVerification
        fields = ('aadhaar_number', 'pan_number')


class BuyerSerializer(BaseUserSerializer):
    """
    Serializer for buyer model.
    """
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')
    username = serializers.CharField(source='user.username')
    password = serializers.CharField(source='user.password', write_only=True)
    verification = BuyerVerificationSerializer(source='buyerverification', read_only=False)
    class Meta(BaseUserSerializer.Meta):
        model = models.Buyer
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'password', 'verification')

    def create(self, validated_data):
        """
        Create a new buyer instance.
        """
        return BaseUserSerializer.create_user(
            validated_data,
            models.Buyer,
            models.BuyerVerification,
            'buyerverification'
        )

    def update(self, instance, validated_data):
        """
        Update an existing buyer instance.
        """
        return BaseUserSerializer.update_user(
            instance,
            validated_data,
            'buyerverification'
        )
