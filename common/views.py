from django.conf import settings
import common.serializer as common_serializer
from .utils.otp_handler import verify_otp, is_ip_throttled, track_ip_request, is_otp_brute_forced, increase_backoff, \
    clear_otp_attempts, can_resend_otp, send_otp, mark_otp_throttle
import rest_framework.status as status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

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

def soft_delete_user(model, username):
    obj = get_object_or_404(model, username=username)
    if hasattr(obj, 'buyer'):
        profile = obj.buyer
        profile.is_deleted = True
        profile.save()
    elif hasattr(obj, 'seller'):
        profile = obj.seller
        profile.is_deleted = True
        profile.save()
    else: return Response({'error': 'User has no profile.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)

def update_user_details(request_data, username, model_class, serializer_class):
    user = get_object_or_404(model_class, username=username)
    if hasattr(user, 'buyer'):
        profile = user.buyer
        if profile.is_deleted: return Response({'error': 'User not found or deleted'}, status=status.HTTP_410_GONE)
    elif hasattr(user, 'seller'):
        profile = user.seller
        if profile.is_deleted: return Response({'error': 'User not found or deleted'}, status=status.HTTP_410_GONE)
    else: return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    data, resp_status = process_serializer(serializer_class, data=request_data, instance=profile)
    return Response(data, status=resp_status)

def add_user(request_data, serializer_class):
    data, resp_status = process_serializer(serializer_class, request_data)
    return Response(data, status=resp_status)

def password_reset(request_data, model_class, frontend_url, serializer_class):
    serializer_instance = serializer_class(data=request_data)
    if not serializer_instance.is_valid(): return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
    email = serializer_instance.validated_data['email']
    try:
        user = model_class.objects.get(email=email)
        success, message = serializer_instance.send_password_reset_email(user, frontend_url)
        if success: return Response({'success': message}, status=status.HTTP_200_OK)
        return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except model_class.DoesNotExist: return Response({'success': 'If email exists, you will receive a password reset email.'}, status=status.HTTP_200_OK)

def password_reset_conformation(request_data, model_class, serializer_class):
    serializer_instance = serializer_class(data=request_data)
    if not serializer_instance.is_valid(): return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
    success, message = serializer_instance.reset_password(model_class)
    if success: return Response({'success': message}, status=status.HTTP_200_OK)
    return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

def user_login(request_data, model_class, serializer_class, user_type_name='user'):
    username = request_data.get('username', '')
    email = request_data.get('email', '')
    password = request_data.get('password', '')
    if username:
        try: user = authenticate(email=model_class.objects.get(username=username).email, password=password)
        except model_class.DoesNotExist: return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    elif email: user = authenticate(email=email, password=password)
    else: return Response({'error': 'Username or password is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if user:
        try:
            if user_type_name == 'buyer':
                if hasattr(user, 'buyer'): profile = user.buyer
                else: return Response({'error': 'You are not registered as a buyer.'}, status=status.HTTP_400_BAD_REQUEST)
            elif user_type_name == 'seller':
                if hasattr(user, 'seller'): profile = user.seller
                else: return Response({'error': 'You are not registered as a seller.'}, status=status.HTTP_400_BAD_REQUEST)
            else: return Response({'error': 'Invalid User Type'}, status=status.HTTP_400_BAD_REQUEST)
            if not profile.is_verified: return Response({'error': 'Your profile is not verified.'}, status=status.HTTP_403_FORBIDDEN)
            if profile.is_deleted: return Response({'error': 'Your account does not exist.'}, status=status.HTTP_410_GONE)
            token, created = Token.objects.get_or_create(user=user)
            serializer = serializer_class(profile)
            return Response({'token': token.key, 'created': created, 'user': serializer.data}, status=status.HTTP_200_OK)
        except AttributeError: return Response({'error': f'You are not registered as a {user_type_name}.'}, status=status.HTTP_400_BAD_REQUEST)
    else: return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

def verify_user(request, email, model_class, user_type='user'):
    otp = request.data.get('otp')
    if request.META.get('HTTP_X_FORWARDED_FOR'): ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    else: ip = request.META.get('REMOTE_ADDR')
    if not (email and otp): return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
    if is_ip_throttled(ip): return Response({'error': 'Too many requests from this IP. Try again.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    track_ip_request(ip)
    if is_otp_brute_forced(email):
        backoff = increase_backoff(email)
        return Response({'error': f'Too many OTP attempts. Try again after {backoff} seconds.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    if not verify_otp(email, otp): return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = model_class.objects.get(email=email)
        user_profile = getattr(user, user_type, None)
        if not user_profile: return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        user_profile.is_verified = True
        clear_otp_attempts(email)
        user_profile.save()
        return Response({'success': 'User successfully verified'}, status=status.HTTP_200_OK)
    except model_class.DoesNotExist:
        clear_otp_attempts(email)
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

def create_user_views(model_class, serializer_class, user_type_name):
    @api_view(['DELETE'])
    def delete_user(r, username): return soft_delete_user(model_class, username)

    @api_view(['PUT', 'PATCH'])
    def update_user(r, username): return update_user_details(r.data, username, model_class, serializer_class)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def add_new_user(r): return add_user(r.data, serializer_class)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def forgot_password(r): return password_reset(r.data, model_class, settings.FRONTEND_URL,
                                                  common_serializer.PasswordResetRequestSerializer)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def reset_password(r): return password_reset_conformation(r.data, model_class,
                                                              common_serializer.PasswordResetConfirmSerializer)

    @api_view(['PUT', 'PATCH'])
    @permission_classes([AllowAny])
    def login(r): return user_login(r.data, model_class, serializer_class, user_type_name)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def verify(r, email): return verify_user(r, email, model_class, user_type_name)

    return {
        'delete_user': delete_user,
        'update_user': update_user,
        'add_user': add_new_user,
        'forgot_password': forgot_password,
        'reset_password': reset_password,
        'login': login,
        'verify': verify,
    }
