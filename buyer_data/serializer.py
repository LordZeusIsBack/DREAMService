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
    verification = BuyerVerificationSerializer(source='buyerverification', read_only=False)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
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

class PurchasedEstateSerializer(serializers.ModelSerializer):
    """
    Serializer for purchased estate model.
    """
    estate_name = serializers.CharField(source='estate.estate_name', read_only=True)
    estate_slug = serializers.SlugField(source='estate.slug', read_only=True)
    purchase_price = serializers.DecimalField(decimal_places=2, max_digits=12, read_only=True)
    purchased_on = serializers.DateTimeField(source='purchase_date', read_only=True)

    class Meta:
        model = models.PurchasedEstate
        fields = ['id', 'estate', 'estate_name', 'estate_slug', 'purchase_price', 'purchased_on', 'transaction_id']
        extra_kwargs = {
            'estate': {'write_only': True},
            'transaction_id': {'write_only': True}
        }

    def validate(self, data):
        buyer = self.context['request'].user.buyer
        estate = data.get('estate')
        if models.PurchasedEstate.objects.filter(buyer=buyer, estate=estate).exists(): raise serializers.ValidationError("You have already purchased this estate.")
        if estate.status != 'available': raise serializers.ValidationError("This estate is not available for purchase.")
        return data

    def create(self, validated_data):
        buyer = self.context['request'].user.buyer
        estate = validated_data.get('estate')
        transaction_id = validated_data.get('transaction_id')
        purchase_price = estate.estate_price

        estate.status = 'sold'
        estate.save()

        return models.PurchasedEstate.objects.create(
            buyer=buyer,
            estate=estate,
            purchase_price=purchase_price,
            transaction_id=transaction_id
        )

    def update(self, instance, validated_data):
        if 'transaction_id' in validated_data and instance.transaction_id != validated_data['transaction_id']: raise serializers.ValidationError({'transaction_id': 'Cannot modify transaction_id once set.'})
        return super().update(instance, validated_data)
