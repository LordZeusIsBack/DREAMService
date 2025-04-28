from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
import seller_data.models as models
import seller_data.serializer as seller_serializer
import common.serializer as common_serializer
from common.views import process_serializer

# Create your views here.
@api_view(['GET'])
def seller_data(r, seller_username): return Response(seller_serializer.SellerSerializer(get_object_or_404(models.Seller, username=seller_username, is_deleted=False)).data)

@api_view(['PUT', 'PATCH'])
def update_seller_data(r, seller_username):
    seller = get_object_or_404(models.Seller, username=seller_username, is_deleted=False)
    data, resp_status = process_serializer(seller_serializer.SellerSerializer, r.data, instance=seller)
    return Response(data, status=resp_status)

@api_view(['POST'])
def add_seller(r):
    data, resp_status = process_serializer(seller_serializer.SellerSerializer, data=r.data)
    return Response(data, status=resp_status)

@api_view(['DELETE'])
def delete_seller(r, seller_username):
    obj = get_object_or_404(models.Seller, username=seller_username, is_deleted=False)
    obj.is_deleted = True
    obj.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(r):
    serializer_instance = common_serializer.PasswordResetRequestSerializer(data=r.data)
    if not serializer_instance.is_valid(): return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
    email = serializer_instance.validated_data['email']
    try:
        seller = models.Seller.objects.get(email=email, is_deleted=False)
        success, message = serializer_instance.send_password_reset_email(seller, settings.FRONTEND_URL)
        if success: return Response({'success': message}, status=status.HTTP_200_OK)
        return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except models.Seller.DoesNotExist: return Response({'success': 'If the email is registered, you will receive a password reset email.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(r):
    serializer_instance = common_serializer.PasswordResetConfirmSerializer(data=r.data)
    if not serializer_instance.is_valid(): return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
    success, message = serializer_instance.reset_password(models.Seller)
    if success: return Response({'success': message}, status=status.HTTP_200_OK)
    return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def seller_login(r):
    username = r.data.get('username', '')
    email = r.data.get('email', '')
    password = r.data.get('password', '')
    user = None
    if username: user = authenticate(username=username, password=password)
    elif email:
        try: user = authenticate(username=models.Seller.objects.get(email=email).username, password=password)
        except models.Seller.DoesNotExist: pass
    else: return Response({'error': 'Username or email is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if user:
        try:
            seller = models.Seller.objects.get(id=user.id)
            if not seller.is_verified: return Response({'error': 'You are not verified.'}, status=status.HTTP_400_BAD_REQUEST)
            if seller.is_deleted: return Response({'error': 'Your account has been deleted.'}, status=status.HTTP_400_BAD_REQUEST)
            token, created = Token.objects.get_or_create(user=user)
            serializer = seller_serializer.SellerSerializer(seller)
            return Response({
                'token': token.key,
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        except models.Seller.DoesNotExist: return Response({'error': 'You are not registered as a seller.'}, status=status.HTTP_401_UNAUTHORIZED)
    else: return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
