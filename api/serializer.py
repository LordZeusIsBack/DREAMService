from rest_framework import serializers
import api.models as models


class SellerVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SellerVerification
        fields = ('gstin', 'aadhaar_number', 'pan_number')


class SellerSerializer(serializers.ModelSerializer):
    verification = SellerVerificationSerializer(source='sellerverification', read_only=True)
    class Meta:
        model = models.Seller
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'username', 'business_name', 'verification')
