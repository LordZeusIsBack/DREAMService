import rest_framework.status as status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
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

def soft_delete_user(model, username):
    obj = get_object_or_404(model, username=username)
    obj.is_deleted = True
    obj.save()
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
    user = None
    if username: user = authenticate(username=username, password=password)
    elif email:
        try: user = authenticate(username=model_class.objects.get(email=email).username, password=password)
        except model_class.DoesNotExist: pass
    else: return Response({'error': 'Username or password is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if user:
        try:
            user_profile = model_class.objects.get(id=user.id)
            if hasattr(user_profile, 'is_verified') and user_profile.is_verified:return Response({'error': 'You are already verified.'}, status=status.HTTP_400_BAD_REQUEST)
            if user_profile.is_deleted: return Response({'error': 'Your account has been deleted.'}, status=status.HTTP_400_BAD_REQUEST)
            token, created = Token.objects.get_or_create(user=user)
            serializer = serializer_class(user)
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
        except model_class.DoesNotExist: return Response({'error': f'You are not registered as a {user_type_name}.'}, status=status.HTTP_400_BAD_REQUEST)
    else: return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
