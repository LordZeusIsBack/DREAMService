from django.conf import settings
import common.serializer as common_serializer
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

def handle_password_reset(request_data, model_class, frontend_url, serializer_class):
    serializer_instance = serializer_class(data=request_data)
    if not serializer_instance.is_valid(): return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
    email = serializer_instance.validated_data['email']
    try:
        user = model_class.objects.get(email=email)
        success, message = serializer_instance.send_password_reset_email(user, frontend_url)
        if success: return Response({'success': message}, status=status.HTTP_200_OK)
        return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except model_class.DoesNotExist: return Response({'success': 'If email exists, you will receive a password reset email.'}, status=status.HTTP_200_OK)

def handle_password_reset_conformation(request_data, model_class, serializer_class):
    serializer_instance = serializer_class(data=request_data)
    if not serializer_instance.is_valid(): return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
    success, message = serializer_instance.reset_password(model_class)
    if success: return Response({'success': message}, status=status.HTTP_200_OK)
    return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

def handle_user_login(request_data, model_class, serializer_class, user_type_name='user'):
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

def create_user_views(model_class, serializer_class, user_type_name):
    @api_view(['DELETE'])
    def delete_user(r, username): return soft_delete_user(model_class, username)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def forgot_password(r): return handle_password_reset(r.data, model_class, settings.FRONTEND_URL, common_serializer.PasswordResetRequestSerializer)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def reset_password(r): return handle_password_reset_conformation(r.data, model_class, common_serializer.PasswordResetConfirmSerializer)

    @api_view(['PUT', 'PATCH'])
    @permission_classes([AllowAny])
    def login(r): return handle_user_login(r.data, model_class, serializer_class, user_type_name)

    return {
        'delete_user': delete_user,
        'forgot_password': forgot_password,
        'reset_password': reset_password,
        'login': login
    }
