from rest_framework import serializers
from common.serializer import BaseUserSerializer
import buyer_data.models as models


class BuyerVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for buyer verification.
    """
    aadhaar_number = serializers.IntegerField()
    pan_number = serializers.CharField()
    aadhaar_card = serializers.ImageField(required=False)
    pan_card = serializers.ImageField(required=False)
    class Meta:
        model = models.BuyerVerification
        fields = ('aadhaar_number', 'pan_number', 'aadhaar_card', 'pan_card')


class BuyerSerializer(BaseUserSerializer):
    """
    Serializer for buyer model.
    """
    aadhaar_number = serializers.IntegerField(write_only=True)
    pan_number = serializers.CharField(write_only=True)
    aadhaar_card = serializers.ImageField(required=False, write_only=True)
    pan_card = serializers.ImageField(required=False, write_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    profile_picture = serializers.ImageField(required=False)
    class Meta(BaseUserSerializer.Meta):
        model = models.Buyer
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'password', 'aadhaar_number',
                  'pan_number', 'aadhaar_card', 'pan_card', 'profile_picture')

    def create(self, validated_data):
        """
        Creates a new buyer along with associated verification data.
        
        Returns:
            Buyer: The newly created buyer instance.
        """
        verification_data = {
            'aadhaar_number': validated_data.pop('aadhaar_number'),
            'pan_number': validated_data.pop('pan_number'),
            'aadhaar_card': validated_data.pop('aadhaar_card', None),
            'pan_card': validated_data.pop('pan_card', None),
        }
        validated_data['buyerverification'] = verification_data
        return BaseUserSerializer.create_user(
            validated_data,
            models.Buyer,
            models.BuyerVerification,
            'buyerverification'
        )

    def update(self, instance, validated_data):
        """
        Updates a buyer and associated verification details.
        
        Delegates the update operation to the base user serializer, ensuring both buyer and verification data are updated together.
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
        """
        Validates that the buyer has not already purchased the estate and that the estate is available for purchase.
        
        Raises a validation error if the buyer has previously purchased the estate or if the estate is not currently available.
        """
        buyer = self.context['request'].user.buyer
        estate = data.get('estate')
        if models.PurchasedEstate.objects.filter(buyer=buyer, estate=estate).exists(): raise serializers.ValidationError("You have already purchased this estate.")
        if estate.status != 'available': raise serializers.ValidationError("This estate is not available for purchase.")
        return data

    def create(self, validated_data):
        """
        Creates a PurchasedEstate record for the current buyer and marks the estate as sold.
        
        Retrieves the buyer from the request context, updates the estate's status to 'sold', and creates a PurchasedEstate instance with the associated buyer, estate, purchase price, and transaction ID.
        """
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
        """
        Updates a PurchasedEstate instance, preventing changes to the transaction ID.
        
        Raises a validation error if an attempt is made to modify the transaction ID after it has been set; otherwise, updates the instance with the provided data.
        """
        if 'transaction_id' in validated_data and instance.transaction_id != validated_data['transaction_id']: raise serializers.ValidationError({'transaction_id': 'Cannot modify transaction_id once set.'})
        return super().update(instance, validated_data)
