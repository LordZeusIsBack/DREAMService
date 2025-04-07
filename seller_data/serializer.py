from rest_framework import serializers
import seller_data.models as models
from rest_framework.exceptions import ValidationError


class SellerVerificationSerializer(serializers.ModelSerializer):
    gstin = serializers.IntegerField()
    aadhaar_number = serializers.IntegerField()
    pan_number = serializers.CharField()
    class Meta:
        model = models.SellerVerification
        fields = ('gstin', 'aadhaar_number', 'pan_number')


class SellerSerializer(serializers.ModelSerializer):
    verification = SellerVerificationSerializer(source='sellerverification', read_only=False)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = models.Seller
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'business_name', 'password',
                  'verification')

    def create(self, validated_data):
        verification_data = validated_data.pop('sellerverification', None)
        password = validated_data.pop('password', None)
        if not (password and verification_data):
            return ValidationError({'error': 'Both password and verification data are required.'})
        seller = models.Seller.objects.create(**validated_data)
        seller.set_password(password)
        seller.save()
        models.SellerVerification.objects.create(seller=seller, **verification_data)
        return seller

    def update(self, instance, validated_data):
        validated_data.pop('sellerverification', None)
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        instance.save()
        return instance
