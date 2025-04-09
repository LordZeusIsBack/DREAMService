from rest_framework import serializers
from common.serializer import BaseUserSerializer
import buyer_data.models as models


class BuyerVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for buyer verification.
    """
    aadhaar_card = serializers.IntegerField()
    pan_number = serializers.CharField()
    class Meta:
        model = models.BuyerVerification
        fields = ('aadhaar_number', 'pan_number')


class BuyerSerializer(BaseUserSerializer):
    """
    Serializer for buyer model.
    """
    verification = BuyerVerificationSerializer(source='buyerverification', read_only=False)
    class Meta(BaseUserSerializer.Meta):
        model = models.Buyer
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'password', 'verification')

    def create(self, validated_data):
        """
        Create a new buyer instance.
        """
        return self.create_user(
            validated_data,
            models.Buyer,
            models.BuyerVerification,
            'verification'
        )
