from common.models import CustomUser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

class BaseUserSerializer(serializers.ModelSerializer):
    """
    Base seller_serializer for user models.
    """
    password = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField()

    class Meta:
        abstract = True

    @staticmethod
    def create_user(validated_data, user_model, verification_model, verification_field):
        """
        Creates a new user along with associated verification data.
        
        Args:
            validated_data: Dictionary containing user details, password, and verification data.
            user_model: The model class for the user profile to be created.
            verification_model: The model class for storing verification information.
            verification_field: The key in validated_data for verification data.
        
        Returns:
            The created user_model instance.
        
        Raises:
            ValidationError: If password or verification data is missing.
        """
        user_data = validated_data.pop('user')
        verification_data = validated_data.pop(verification_field, None)
        password = validated_data.pop('password', None)
        if not (password and verification_data): raise ValidationError({'error': 'Both password and verification data are required.'})
        custom_user_instance = CustomUser.objects.create_user(
            email=user_data['email'],
            username=user_data['username'],
            password=password,
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        user_model_instance = user_model.objects.create(user=custom_user_instance, **validated_data)
        verification_model.objects.create(**{user_model.__name__.lower(): user_model_instance}, **verification_data)
        return user_model_instance

    @staticmethod
    def update_user(instance, validated_data, verification_field):
        """
        Updates a user model instance and its related user account with new data.
        
        The function updates the attributes of the related user account, including setting a new password if provided, and then updates the main instance's attributes. The verification field is ignored during the update.
        
        Args:
            instance: The user model instance to update.
            validated_data: Dictionary containing updated data, including nested user data.
            verification_field: The key for verification data to exclude from updates.
        
        Returns:
            The updated user model instance.
        """
        user_data = validated_data.pop('user')
        validated_data.pop(verification_field, None)
        new_password = validated_data.pop('password', None)
        user_instance = instance.user
        for attr, value in user_data.items(): setattr(user_instance, attr, value)
        if new_password: user_instance.set_password(new_password)
        user_instance.save()
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        instance.save()
        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset email.
    """
    email = serializers.EmailField()

    @staticmethod
    def send_password_reset_email(user, frontend_url):
        """
        Sends a password reset email with a secure token and reset link to the user.
        
        Args:
            user: The user instance to receive the reset email.
            frontend_url: The base URL of the frontend application for constructing the reset link.
        
        Returns:
            A tuple (success, message) where success is True if the email was sent, or False with an error message otherwise.
        """
        try:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"
            send_mail(
                'Password Reset Request',
                f'Hello {user.first_name} {user.last_name},\n\n'
                f'You requested a password reset for your account. '
                f'Please click the following link to set a new password:\n\n'
                f'{reset_link}\n\n'
                f'This link will expire in 1 hour.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
            return True, 'Password reset mail has been sent!'
        except Exception as e: return False, str(e)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a password reset."""
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, required=True)

    @staticmethod
    def validate_password(value):
        """
        Validates the new password.
        """
        if len(value) < 8: raise serializers.ValidationError('Password must be at least 8 characters long.')
        return value

    def reset_password(self, user_model):
        """
        Resets a user's password using a UID and token.
        
        Attempts to set a new password for the user identified by the provided UID if the token is valid. Returns a tuple indicating success or failure and a corresponding message.
        
        Args:
            user_model: The user model class to query for the user instance.
        
        Returns:
            A tuple (success: bool, message: str) indicating the result of the password reset attempt.
        """
        uid = self.validated_data['uid']
        token = self.validated_data['token']
        new_password = self.validated_data['password']
        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = user_model.objects.get(pk=pk)
            if not default_token_generator.check_token(user, token): return False , 'Invalid token or expired link.'
            user.set_password(new_password)
            user.save()
            return True, 'Your Password has been successfully changed!'
        except (TypeError, ValueError, OverflowError, user_model.DoesNotExist): return False, 'Invalid token or expired link.'
        except Exception as e: return False, str(e)
