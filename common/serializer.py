from common.models import CustomUser
from .tasks import send_mail_containing_otp
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.db.transaction import atomic, on_commit

class BaseUserSerializer(serializers.ModelSerializer):
    """
    Base seller_serializer for user models.
    """
    password = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.IntegerField(required=False)
    aadhaar_number = serializers.IntegerField(required=False, read_only=True)
    pan_number = serializers.CharField(required=False, read_only=True)

    class Meta:
        abstract = True

    @staticmethod
    def create_user(validated_data, user_model, verification_model, verification_field):
        """
        Creates a new user and an associated verification record within a database transaction, sending an OTP to the user's email.
        
        Parameters:
            validated_data (dict): Contains nested user data, password, and verification information.
            user_model: The model class for the user profile to be created.
            verification_model: The model class for the verification record to be created.
            verification_field (str): The key in validated_data containing verification data.
        
        Returns:
            An instance of the created user model.
        
        Raises:
            ValidationError: If required password or verification data is missing, or if any error occurs during creation or validation.
        """
        user_data = validated_data.pop('user')
        verification_data = validated_data.pop(verification_field)
        password = validated_data.pop('password', None)
        if not (password and verification_data): raise ValidationError({'error': 'Both password and verification data are required.'})
        try:
            with atomic():
                custom_user_instance = CustomUser.objects.create_user(
                    email=user_data['email'],
                    username=user_data['username'],
                    password=password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                user_model_instance = user_model.objects.create(user=custom_user_instance, **validated_data)
                try: user_model_instance.full_clean()
                except Exception as e: raise ValidationError({'error': str(e)}) from e
                verification_model.objects.create(**{user_model.__name__.lower(): user_model_instance}, **verification_data)
                on_commit(lambda: send_mail_containing_otp.delay(email=custom_user_instance.email))
                return user_model_instance
        except Exception as e: raise ValidationError({'error': str(e)}) from e

    @staticmethod
    def update_user(instance, validated_data, verification_field):
        """
        Updates an existing user and related instance with validated data, enforcing immutability of the phone number and preventing changes to Aadhaar and PAN numbers.
        
        Raises:
            ValidationError: If attempting to change the phone number or if data validation fails.
        
        Returns:
            The updated instance after applying changes and validation.
        """
        if 'phone_number' in validated_data and validated_data['phone_number'] != instance.phone_number: raise ValidationError({'error': 'Phone number once set cannot be changed!'})
        user_data = validated_data.pop('user')
        validated_data.pop('aadhaar_number', None)
        validated_data.pop('pan_number', None)
        new_password = validated_data.pop('password', None)
        user_instance = instance.user
        for attr, value in user_data.items(): setattr(user_instance, attr, value)
        if new_password: user_instance.set_password(new_password)
        user_instance.save()
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        try: instance.full_clean()
        except Exception as e: raise ValidationError({'error': str(e)}) from e
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
