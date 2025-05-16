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
        Create a new user instance.
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
        Update an existing user instance.
        """
        validated_data.pop(verification_field, None)
        new_password = validated_data.pop('password', None)
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        if new_password: instance.set_password(new_password)
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
        Sends a password reset email to the user with a secure token.
        :param user: The user instance (Seller or Buyer).
        :param frontend_url: The frontend URL where the reset link will redirect.
        """
        try:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"
            send_mail(
                'Password Reset Request',
                f'Hello {user.get_full_name()},\n\n'
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
        uid = self.validated_data['uid']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']
        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = user_model.objects.get(pk=pk)
            if not default_token_generator.check_token(user, token): return False , 'Invalid token or expired link.'
            user.set_password(new_password)
            user.save()
            return True, 'Your Password has been successfully changed!'
        except (TypeError, ValueError, OverflowError, user_model.DoesNotExist): return False, 'Invalid token or expired link.'
        except Exception as e: return False, str(e)
