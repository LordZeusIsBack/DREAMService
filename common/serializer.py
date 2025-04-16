from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import rest_framework.status as status
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from rest_framework.response import Response

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
            token = default_token_generator(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"
            send_mail(
                'Password Reset Request',
                f'Hello {user.get_full_name()},\n\n'
                f'You requested a password reset for your account. '
                f'Please click the following link to set a new password:\n\n'
                f'{reset_link}\n\n'
                f'This link will expire in 24 hours.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
            return Response({'success': 'Password reset mail has been sent!'}, status=status.HTTP_200_OK)
        except Exception as e: return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a password reset."""
    uid, token, new_password = serializers.CharField(), serializers.CharField(), serializers.CharField(write_only=True)

    @staticmethod
    def validate_password(value):
        """
        Validates the new password.
        """
        if len(value) < 8: raise serializers.ValidationError('Password must be at least 8 characters long.')
        return value

    def reset_password(self, user_model):
        uid, token, password = self.validated_data['uid'], self.validated_data['token'], self.validated_data['password']
        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = user_model.objects.get(pk=pk)
            if not default_token_generator.check_token(user, token): return Response({'error': 'Invalid token or expired link.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()
            return Response({'success': 'Your Password has been successfully changed!'}, status=status.HTTP_200_OK)
        except (TypeError, ValueError, OverflowError, user_model.DoesNotExist): return Response({'error': 'Invalid token or expired link.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
