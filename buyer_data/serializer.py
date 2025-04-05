from rest_framework import serializers
import buyer_data.models as models


class BuyerVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BuyerVerification
        fields = ('aadhaar_number', 'pan_number')


class BuyerSerializer(serializers.ModelSerializer):
    verification = BuyerVerificationSerializer(source='buyerverification', read_only=True)
    class Meta:
        model = models.Buyer
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'verification')
