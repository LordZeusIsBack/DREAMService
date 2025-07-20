from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework.parsers import MultiPartParser, FormParser
import common.serializer as common_serializer
from .utils.otp_handler import verify_otp, is_ip_throttled, track_ip_request, is_otp_brute_forced, increase_backoff, clear_otp_attempts, can_resend_otp, send_otp, mark_otp_throttle
import rest_framework.status as status
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes


# Create your views here.
def process_serializer(serializer_class, data, instance=None, success_status=status.HTTP_200_OK, create_status=status.HTTP_201_CREATED):
    """
    Validates and saves data using the specified serializer, supporting both creation and update operations.
    
    Parameters:
        serializer_class: The serializer class used for validation and saving.
        data: The input data to validate and save.
        instance: An existing object to update; if None, a new object is created.
        success_status: HTTP status code for a successful update.
        create_status: HTTP status code for a successful creation.
    
    Returns:
        tuple: A pair containing either serialized data or error details, and the corresponding HTTP status code.
    """
    serializer_instance = serializer_class(instance, data=data) if instance else serializer_class(data=data)
    if serializer_instance.is_valid():
        try:
            serializer_instance.save()
            return serializer_instance.data, (success_status if instance else create_status)
        except Exception as e:
            return {'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    return serializer_instance.errors, status.HTTP_400_BAD_REQUEST

def remove_user_information(model, username):
    """
    Deletes a user object identified by username from the specified model.
    
    Returns:
        Response: HTTP 204 No Content on successful deletion.
    """
    obj = get_object_or_404(model, username=username)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

def update_user_details(request_data, username, model_class, serializer_class):
    """
    Updates a user's buyer or seller profile with the provided data.
    
    If the user or their profile is deleted or missing, returns an appropriate error response. Otherwise, updates the profile using the specified serializer and returns the serialized data with the corresponding HTTP status code.
    """
    user = get_object_or_404(model_class, username=username)
    if hasattr(user, 'buyer'):
        profile = user.buyer
    elif hasattr(user, 'seller'):
        profile = user.seller
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
    """
    Handles password reset confirmation by validating input data and resetting the user's password.
    
    Validates the provided data using the given serializer. If valid, attempts to reset the password for the user in the specified model. Returns a success response if the password is reset, or an error response if the operation fails.
    """
    serializer_instance = serializer_class(data=request_data)
    if not serializer_instance.is_valid(): return Response(serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
    success, message = serializer_instance.reset_password(model_class)
    if success: return Response({'success': message}, status=status.HTTP_200_OK)
    return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

def user_login(request, model_class, user_type_name='user'):
    """
    Authenticates a user by username or email and password, verifies user type and profile status, and logs the user in via Django session.
    
    Checks for required credentials and validates that the user account is active and associated with the specified user type (buyer or seller). Ensures the user's profile is verified before allowing login. On successful authentication, logs in the user and returns a success response with the user's email and a CSRF token. Returns appropriate error responses for missing credentials, inactive accounts, invalid credentials, incorrect user type, or unverified profiles.
    """
    username = request.data.get('username', '')
    email = request.data.get('email', '')
    password = request.data.get('password', '')
    if not password: return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        if username: user_obj = model_class.objects.get(username=username)
        elif email: user_obj = model_class.objects.get(email=email)
        else: return Response({'error': 'Username or email is required.'}, status=status.HTTP_400_BAD_REQUEST)
    except model_class.DoesNotExist: return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user_obj.is_active: return Response({'error': 'Account is deactivated. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)
    user = authenticate(email=user_obj.email, password=password)
    if user:
        if user_type_name == 'buyer':
            if hasattr(user, 'buyer'): profile = user.buyer
            else: return Response({'error': 'You are not registered as a buyer.'}, status=status.HTTP_400_BAD_REQUEST)
        elif user_type_name == 'seller':
            if hasattr(user, 'seller'): profile = user.seller
            else: return Response({'error': 'You are not registered as a seller.'}, status=status.HTTP_400_BAD_REQUEST)
        else: return Response({'error': 'Invalid user type.'}, status=status.HTTP_400_BAD_REQUEST)
        if not profile.is_verified: return Response({'error': 'User is not verified.'}, status=status.HTTP_403_FORBIDDEN)
        login(request, user)
        return Response({
            'success': True,
            'message': 'Login successful.',
            'email': user.get_username(),
            'csrf_token': get_token(request)
        }, status=status.HTTP_200_OK)
    else: return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

def verify_user(request, email, model_class, user_type='user'):
    """
    Verifies a user's OTP for account activation, enforcing IP-based throttling and brute force protection.
    
    Checks the provided OTP for the given email address and user type. If the OTP is valid and verification limits are not exceeded, marks the user's profile as verified. Returns a success response on verification or an error response if the OTP is invalid, expired, or if throttling/brute force limits are reached.
    
    Parameters:
        email (str): The email address of the user to verify.
        user_type (str, optional): The user profile type to verify (default is 'user').
    
    Returns:
        Response: A DRF Response indicating the result of the verification attempt.
    """
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

def resend_user_otp(request, email, model_class, user_type='user'):
    """
    Resends a verification OTP to the user's email address, enforcing IP-based throttling and cooldown restrictions.
    
    If the request is allowed, a new OTP is sent to the specified email. Returns error responses if rate limits are exceeded, the cooldown period has not elapsed, the user profile is missing, or an unexpected error occurs.
    """
    if request.META.get('HTTP_X_FORWARDED_FOR'): ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    else: ip = request.META.get('REMOTE_ADDR')
    if is_ip_throttled(ip): return Response({'error': 'Too many requests from this IP. Try again.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    track_ip_request(ip)
    if not can_resend_otp(email): return Response({'error': 'You can only resend OTP after cooldown period.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    try:
        user = model_class.objects.get(email=email)
        user_profile = getattr(user, user_type)
        if not user_profile: return Response({'error': 'Unable to send OTP. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)
        send_otp(email, is_resend=True)
        return Response({'success': 'If this email is registered, an OTP has been sent.'}, status=status.HTTP_200_OK)
    except model_class.DoesNotExist:
        mark_otp_throttle(email, cooldown=30)
        return Response({'error': 'User profile not found'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e: return Response({'error': 'Please wait before requesting another OTP.', 'message': str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    except Exception as e: return Response({'error':'Unable to send OTP. Please try again later.', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def log_user_out(request):
    """
    Logs out the current user and returns a success response.
    
    Returns:
        Response: A response indicating successful logout with HTTP 200 status.
    """
    logout(request)
    return Response({'success': 'User logged out successfully.'}, status=status.HTTP_200_OK)

def create_user_views(model_class, serializer_class, user_type_name):
    """
    Creates a dictionary of Django REST framework view functions for user management operations tailored to the specified user model, serializer, and user type.
    
    The returned dictionary includes views for user creation, update, deletion, authentication, password reset, OTP verification, OTP resending, and logout, each configured for use in DRF routing.
    
    Returns:
        dict: Mapping of operation names to their corresponding DRF view functions.
    """
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    def delete_user(r, username):
        """
        Deletes a user identified by username from the database.
        
        Returns:
            Response: HTTP 204 No Content if the user is deleted successfully, or HTTP 404 if the user does not exist.
        """
        return remove_user_information(model_class, username)

    @api_view(['PATCH'])
    @parser_classes([MultiPartParser, FormParser])
    def update_user(r, username):
        """
        Updates the details of a user profile identified by username using the provided request data.

        Parameters:
	        r: The HTTP request containing user data for the update.
	        username (str): The username of the user whose profile is to be updated.

        Returns:
	        Response: A DRF Response object with the updated profile data and status code, or an error response if the update fails.
        """
        return update_user_details(r.data, username, model_class, serializer_class)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    @parser_classes([MultiPartParser, FormParser])
    def add_new_user(r):
        """
        Creates a new user profile using the provided request data and serializer.

        Returns:
	        Response: Serialized user data and HTTP status code indicating the result of the creation.
        """
        return add_user(r.data, serializer_class)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def forgot_password(r):
        """
        Initiate the password reset process for a user by validating the request data and sending a reset email if applicable.
        
        Returns:
            Response: A DRF Response indicating whether the password reset email was sent or if an error occurred.
        """
        return password_reset(r.data, model_class, settings.FRONTEND_URL, common_serializer.PasswordResetRequestSerializer)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def reset_password(r):
        """
        Handles password reset confirmation by validating and applying the new password using the provided request data.
        
        Returns:
            Response: A DRF Response object indicating success or failure of the password reset operation.
        """
        return password_reset_conformation(r.data, model_class, common_serializer.PasswordResetConfirmSerializer)

    @api_view(['PUT', 'PATCH'])
    @permission_classes([AllowAny])
    def login_user(r):
        """
        Authenticates a user using the provided request and establishes a session.
        
        Returns:
            Response with a success message, user's email, and CSRF token on successful login, or an error response on failure.
        """
        return user_login(r, model_class, user_type_name)

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def user_logout(r):
        """
        Logs out the current user and returns a success response.
        """
        return log_user_out(r)

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def verify(r, email):
        """
        Verifies a user's OTP using the provided email address.

        Delegates to the `verify_user` function with the specified model and user type.
        """
        return verify_user(r, email, model_class, user_type_name)

    @api_view(['GET'])
    @permission_classes([AllowAny])
    def resend_otp(r, email):
        """
        Resend a one-time password (OTP) to the user's email address with rate limiting and cooldown enforcement.

        Parameters:
            email (str): The email address of the user to receive the OTP.

        Returns:
            Response: A Django REST framework response indicating success or the reason for failure (e.g., throttling, cooldown, or user not found).
        """
        return resend_user_otp(r, email, model_class, user_type_name)

    return {
        'delete_user': delete_user,
        'update_user': update_user,
        'add_user': add_new_user,
        'forgot_password': forgot_password,
        'reset_password': reset_password,
        'login': login_user,
        'logout': user_logout,
        'verify': verify,
        'resend_otp': resend_otp
    }
