import rest_framework.status as status
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from rest_framework.response import Response


# Create your views here.
def process_serializer(serializer_class, data, instance=None, success_status=status.HTTP_200_OK, create_status=status.HTTP_201_CREATED):
    serializer_instance = serializer_class(instance, data=data) if instance else serializer_class(data=data)
    if serializer_instance.is_valid():
        try:
            serializer_instance.save()
            return serializer_instance.data, (success_status if instance else create_status)
        except Exception as e:
            return {'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    return serializer_instance.errors, status.HTTP_400_BAD_REQUEST

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
    except Exception: return status.HTTP_500_INTERNAL_SERVER_ERROR

def reset_user_password(uid, token, new_password, user_model):
    """
    Resets the user's password after verifying the token.
    :param uid: Base64-encoded user ID.
    :param token: Secure token for password reset.
    :param new_password: The new password to set.
    :param user_model: The model class (e.g., Seller or Buyer).
    """
    try:
        pk = force_str(urlsafe_base64_decode(uid))
        user = user_model.objects.get(pk=pk)
        if not default_token_generator.check_token(user, token): return Response({'error': 'Invalid token or expired link.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'success': 'Your Password has been successfully changed!'}, status=status.HTTP_200_OK)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist): return Response({'error': 'Invalid token or expired link.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception: return status.HTTP_500_INTERNAL_SERVER_ERROR
