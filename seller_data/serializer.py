from rest_framework import serializers
import seller_data.models as models


class SellerVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SellerVerification
        fields = ('gstin', 'aadhaar_number', 'pan_number')


class SellerSerializer(serializers.ModelSerializer):
    verification = SellerVerificationSerializer(source='sellerverification', read_only=True)
    class Meta:
        model = models.Seller
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'business_name', 'verification')
