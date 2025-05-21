from django.urls import path

def create_user_url_patterns(view_module, user_type):
    view_name = 'view_buyer' if user_type == 'buyer' else 'view_seller'
    update_name = 'update_buyer' if user_type == 'buyer' else 'update_seller'
    forgot_name = f'{user_type}_forgot_password' if user_type == 'buyer' else f'{user_type}_forgot_password'
    reset_name = f'{user_type}_reset_password' if user_type == 'buyer' else f'{user_type}_reset_password'

    return [
        path(f'view-{user_type}/<str:{user_type}_username>', getattr(view_module, f'{user_type}_data'), name=view_name),
        path(f'update-{user_type}/<str:username>', getattr(view_module, f'update_{user_type}_data'), name=update_name),
        path(f'add-{user_type}', getattr(view_module, f'add_{user_type}'), name=f'add_{user_type}'),
        path(f'delete-{user_type}/<str:{user_type}_username>', getattr(view_module, f'delete_{user_type}'), name=f'delete_{user_type}'),
        path('forgot-password/', getattr(view_module, f'{user_type}_forgot_password'), name=forgot_name),
        path('reset-password/', getattr(view_module, f'{user_type}_reset_password'), name=reset_name),
        path(f'{user_type}-login/', getattr(view_module, f'{user_type}_login'), name=f'{user_type}_login'),
    ]
