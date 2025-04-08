from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import seller_data.serializer as serializer
import seller_data.models as models
import rest_framework.status as status
from django.shortcuts import get_object_or_404
from common.views import process_serializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny

# Create your views here.
@api_view(['GET'])
def seller_data(r, seller_id): return Response(serializer.SellerSerializer(get_object_or_404(models.Seller, id=seller_id, is_deleted=False)).data)

@api_view(['PUT', 'PATCH'])
def update_seller_data(r, seller_id):
    seller = get_object_or_404(models.Seller, id=seller_id)
    data, resp_status = process_serializer(serializer.SellerSerializer, r.data, instance=seller)
    return Response(data, status=resp_status)

@api_view(['POST'])
def add_seller(r):
    data, resp_status = process_serializer(serializer.SellerSerializer, data=r.data)
    return Response(data, status=resp_status)

@api_view(['DELETE'])
def delete_seller(r, seller_id):
    obj = get_object_or_404(models.Seller, id=seller_id)
    obj.is_deleted = True
    obj.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Initiate password reset process when a Seller forgets their password.
    Sends an email with a reset link containing a secure token.
    """
    email = request.data.get('email')

    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Find the seller by email
        seller = models.Seller.objects.get(email=email)

        # Generate secure token
        token = default_token_generator.make_token(seller)
        uid = urlsafe_base64_encode(force_bytes(seller.pk))

        # Create reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        # Send email with reset link
        send_mail(
            'Password Reset Request',
            f'Hello {seller.business_name},\n\n'
            f'You requested a password reset for your account. '
            f'Please click the following link to set a new password:\n\n'
            f'{reset_link}\n\n'
            f'This link will expire in 24 hours.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response(
            {'success': 'Password reset email has been sent'},
            status=status.HTTP_200_OK
        )

    except models.Seller.DoesNotExist:
        # For security, don't reveal whether an email exists
        return Response(
            {'success': 'If the email exists, a password reset link has been sent'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': 'An error occurred while processing your request'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
