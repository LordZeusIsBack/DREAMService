from django.urls import path

def create_user_url_patterns(view_module, user_type):
    """
    Generate Django URL patterns for user operations based on the specified user type.
    
    Creates and returns a list of URL pattern objects for either "buyer" or "seller" users, mapping each route to the corresponding view function in the provided view module. The generated patterns include endpoints for viewing, updating, adding, and deleting users; password management; login; email verification; and OTP resending, all tailored to the given user type.
    
    Parameters:
        view_module: The module containing user-related view functions.
        user_type (str): The type of user ("buyer" or "seller") for which to generate URL patterns.
    
    Returns:
        list: Django URL pattern objects for the specified user type.
    """
    view_name = 'view_buyer' if user_type == 'buyer' else 'view_seller'
    update_name = 'update_buyer' if user_type == 'buyer' else 'update_seller'
    forgot_name = f'{user_type}_forgot_password' if user_type == 'buyer' else f'{user_type}_forgot_password'
    reset_name = f'{user_type}_reset_password' if user_type == 'buyer' else f'{user_type}_reset_password'

    return [
        path(f'view-{user_type}/<str:{user_type}_username>', getattr(view_module, f'{user_type}_data'), name=view_name),
        path(f'update-{user_type}/<str:username>', getattr(view_module, f'update_{user_type}_data'), name=update_name),
        path(f'add-{user_type}', getattr(view_module, f'add_{user_type}'), name=f'add_{user_type}'),
        path(f'delete-{user_type}/<str:username>', getattr(view_module, f'delete_{user_type}'), name=f'delete_{user_type}'),
        path('forgot-password', getattr(view_module, f'{user_type}_forgot_password'), name=forgot_name),
        path('reset-password', getattr(view_module, f'{user_type}_reset_password'), name=reset_name),
        path(f'{user_type}-login', getattr(view_module, f'{user_type}_login'), name=f'{user_type}_login'),
        path(f'{user_type}-verify-email/<str:email>', getattr(view_module, f'{user_type}_verify_email'), name=f'{user_type}_email_verification'),
        path('resend-otp/<str:email>', getattr(view_module, f'{user_type}_resend_otp'), name=f'resend_{user_type}_otp'),
    ]
