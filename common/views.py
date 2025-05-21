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
    """
    Marks the user's buyer or seller profile as deleted.
    
    Retrieves a user by username from the specified model and sets the associated buyer or seller profile's `is_deleted` flag to True. Returns HTTP 204 No Content on success, or 404 if the user has no profile.
    """
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

def update_user_details(request_data, username, model_class, serializer_class, lookup_kwargs=None):
    """
    Updates a user's buyer or seller profile with the provided data.
    
    Fetches the user by username and determines the associated buyer or seller profile. If the profile is deleted, returns HTTP 410 Gone. If no profile exists, returns HTTP 404 Not Found. Otherwise, updates the profile using the serializer and returns the serialized data with the appropriate status.
    """
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
    """
    Creates a new user profile using the provided serializer and request data.
    
    Args:
        request_data: The data for creating the user profile.
        serializer_class: The serializer class used to validate and save the user data.
    
    Returns:
        A DRF Response containing the serialized user data and the appropriate HTTP status code.
    """
    data, resp_status = process_serializer(serializer_class, request_data)
    return Response(data, status=resp_status)

def password_reset(request_data, model_class, frontend_url, serializer_class):
    """
    Handles password reset requests by validating input and sending a reset email if the user exists.
    
    Validates the provided email address and, if a user with that email exists, sends a password reset email using the serializer's method. Always returns a generic success message to prevent information disclosure about user existence. Returns 500 if email sending fails.
    """
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
    """
    Confirms a password reset by validating input and updating the user's password.
    
    Validates the provided data using the serializer. If valid, attempts to reset the user's password via the serializer's `reset_password` method. Returns a success message with HTTP 200 on success, or an error message with HTTP 400 on failure.
    """
    serializer_instance = serializer_class(data=request_data)
    if not serializer_instance.is_valid(): return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
    success, message = serializer_instance.reset_password(model_class)
    if success: return Response({'success': message}, status=status.HTTP_200_OK)
    return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

def user_login(request_data, model_class, serializer_class, user_type_name='user'):
    """
    Authenticates a user and returns an authentication token and profile data.
    
    Attempts to authenticate a user using the provided username or email and password.
    Verifies that the user has the specified profile type (buyer or seller), that the profile
    is verified and not deleted, and returns an authentication token along with serialized
    profile data on success.
    
    Args:
        request_data: Dictionary containing authentication credentials.
        user_type_name: The expected user profile type ('buyer' or 'seller').
    
    Returns:
        Response containing the authentication token, a flag indicating if the token was
        newly created, and serialized user profile data on success. Returns appropriate
        error responses for invalid credentials, missing or unverified profiles, or deleted accounts.
    """
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
    """
    Creates a dictionary of Django REST framework API views for user management operations.
    
    The returned views handle user deletion (soft delete), update, creation, password reset requests, password reset confirmations, and login for the specified user type. Each view is configured with appropriate HTTP methods and permissions.
    """
    @api_view(['DELETE'])
    def delete_user(r, username): return soft_delete_user(model_class, username)

    @api_view(['PUT', 'PATCH'])
    def update_user(r, username): """
Updates a user's profile details using the provided request data.

Args:
    r: The HTTP request containing user data.
    username: The username identifying the user to update.

Returns:
    A Response object with the updated user data and appropriate HTTP status.
"""
return update_user_details(r.data, username, model_class, serializer_class)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def add_new_user(r): """
Creates a new user profile using the provided request data.

Args:
    r: The HTTP request containing user data in its body.

Returns:
    A Response object with serialized user data and HTTP status code.
"""
return add_user(r.data, serializer_class)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def forgot_password(r): """
                                                  Handles a password reset request by validating input and sending a reset email.
                                                  
                                                  Args:
                                                      r: The incoming HTTP request containing password reset data.
                                                  
                                                  Returns:
                                                      A Response indicating whether the password reset email was sent or if an error occurred.
                                                  """
                                                  return password_reset(r.data, model_class, settings.FRONTEND_URL,
                                                  common_serializer.PasswordResetRequestSerializer)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def reset_password(r): """
                                                              Handles password reset confirmation using the provided request data.
                                                              
                                                              Args:
                                                                  r: The HTTP request containing password reset confirmation data.
                                                              
                                                              Returns:
                                                                  A Response object indicating success or failure of the password reset.
                                                              """
                                                              return password_reset_conformation(r.data, model_class,
                                                              common_serializer.PasswordResetConfirmSerializer)

    @api_view(['PUT', 'PATCH'])
    @permission_classes([AllowAny])
    def login(r): """
Authenticates a user and returns an authentication token and user data.

Delegates to the user_login function, which verifies credentials and user profile
status, then returns an authentication token and serialized user information on
success. Returns appropriate error responses for invalid credentials, missing or
deleted profiles, or unverified accounts.
"""
return user_login(r.data, model_class, serializer_class, user_type_name)

    return {
        'delete_user': delete_user,
        'update_user': update_user,
        'add_user': add_new_user,
        'forgot_password': forgot_password,
        'reset_password': reset_password,
        'login': login
    }
