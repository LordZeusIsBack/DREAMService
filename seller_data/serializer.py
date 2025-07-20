from rest_framework import serializers
import seller_data.models as models
from common.serializer import BaseUserSerializer


class SellerVerificationSerializer(serializers.ModelSerializer):
    gstin = serializers.IntegerField()
    pan_number = serializers.CharField()
    class Meta:
        model = models.SellerVerification
        fields = ('gstin', 'pan_number')


class SellerSerializer(BaseUserSerializer):
    """
    Serializer for seller model.
    """
    pan_number = serializers.CharField(write_only=True)
    pan_card = serializers.ImageField(required=False, write_only=True)
    gstin = serializers.IntegerField(write_only=True)
    agent_rera_id = serializers.SerializerMethodField(read_only=True)
    agent_rera_id_write = serializers.CharField(write_only=True, source='agent_rera_id')
    profile_picture = serializers.ImageField(required=False)
    business_name = serializers.CharField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')

    class Meta(BaseUserSerializer.Meta):
        model = models.Seller
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'business_name', 'username', 'password',
                  'pan_number', 'pan_card', 'gstin', 'agent_rera_id', 'agent_rera_id_write', 'profile_picture')

    @staticmethod
    def get_agent_rera_id(obj):
        """
        Retrieve the agent RERA ID from the related seller verification object.
        
        Returns:
            str or None: The agent RERA ID if available; otherwise, None.
        """
        try: return obj.sellerverification.agent_rera_id
        except AttributeError: return None

    def create(self, validated_data):
        """
        Creates a new Seller instance along with associated SellerVerification data.
        
        Extracts verification-related fields from the validated data, assigns them to the related SellerVerification, and creates both records using the base user serializer.
        """
        verification_data = {
            'pan_number': validated_data.pop('pan_number'),
            'pan_card': validated_data.pop('pan_card', None),
            'gstin': validated_data.pop('gstin'),
            'agent_rera_id': validated_data.pop('agent_rera_id')
        }
        validated_data['sellerverification'] = verification_data
        return BaseUserSerializer.create_user(
            validated_data,
            models.Seller,
            models.SellerVerification,
            'sellerverification'
        )

    def update(self, instance, validated_data):
        """
        Update a seller instance with new data, disallowing changes to the business name once it has been set.
        
        Raises:
            serializers.ValidationError: If an attempt is made to change the business name after it is set.
        
        Returns:
            The updated seller instance.
        """
        if 'business_name' in validated_data and validated_data['business_name'] != instance.business_name: raise serializers.ValidationError({'business_name': 'Cannot modify business_name once set.'})
        return BaseUserSerializer.update_user(
            instance,
            validated_data,
            'sellerverification'
        )
