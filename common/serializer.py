from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class BaseUserSerializer(serializers.ModelSerializer):
    """
    Base serializer for user models.
    """
    password = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField()

    class Meta:
        abstract = True

    @staticmethod
    def create_user(validated_data, user_model, verification_model, verification_field):
        """
        Create a new user instance.
        """
        verification_data = validated_data.pop(verification_field, None)
        password = validated_data.pop('password', None)

        if not (password and verification_data): raise ValidationError({'error': 'Both password and verification data are required.'})
        user_instance = user_model.objects.create(**validated_data)
        user_instance.set_password(password)
        user_instance.save()

        verification_model.objects.create(**{user_model.__name__.lower(): user_instance}, **verification_data)
        return user_instance

    @staticmethod
    def update_user(instance, validated_data, verification_field):
        """
        Update an existing user instance.
        """
        validated_data.pop(verification_field, None)
        new_password = validated_data.pop('password', None)
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        if new_password: instance.set_password(new_password)
        instance.save()
        return instance
