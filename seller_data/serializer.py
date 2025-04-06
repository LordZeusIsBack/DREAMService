from rest_framework import serializers
import seller_data.models as models


class SellerVerificationSerializer(serializers.ModelSerializer):
    gstin = serializers.IntegerField()
    aadhaar_number = serializers.IntegerField()
    pan_number = serializers.CharField()
    class Meta:
        model = models.SellerVerification
        fields = ('gstin', 'aadhaar_number', 'pan_number')


class SellerSerializer(serializers.ModelSerializer):
    verification = SellerVerificationSerializer(source='sellerverification', read_only=False)
    class Meta:
        model = models.Seller
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'business_name', 'verification')

    def create(self, validated_data):
        # Extract nested verification data using the source key 'sellerverification'
        verification_data = validated_data.pop('sellerverification', None)

        # Create the Seller instance using the remaining validated data
        seller = models.Seller.objects.create(**validated_data)

        # If verification data is provided, create the SellerVerification record linked to the seller
        if verification_data:
            models.SellerVerification.objects.create(seller=seller, **verification_data)

        return seller

    def update(self, instance, validated_data):
        validated_data.pop('sellerverification', None)
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        instance.save()
        return instance
