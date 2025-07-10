from functools import wraps
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN
from seller_data.models import SellerSubscription

SUBSCRIPTION_FEATURES = {
    '1': ['basic listing', 'limited support', 'contact form', 'lead button'],
    '2': ['homepage feature', 'walkthrough video', 'social media posts', 'monthly reporting'],
    '3': ['ad campaigns', 'analytics dashboard', 'site visit scheduling', 'email marketing'],
    '4': ['drone shots', 'HD video tours', 'brand page', 'priority support']
}

def require_seller_subscription(min_stage=None, feature=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated: return Response({'detail': 'Login Required'}, status=HTTP_403_FORBIDDEN)
            try:
                seller = user.seller
                subscription = seller.subscription
                user_stage = int(subscription.stage)
            except (AttributeError, SellerSubscription.DoesNotExist): return Response({'detail': 'Subscription Required'}, status=HTTP_403_FORBIDDEN)
            if min_stage and user_stage < int(min_stage): return Response({'detail': f'Upgrade to Stage {min_stage} to access this feature!'}, status=HTTP_403_FORBIDDEN)
            if feature:
                allowed_features = []
                for s in range(1, user_stage + 1):
                    allowed_features += SUBSCRIPTION_FEATURES.get(str(s), [])
                if feature not in allowed_features: return Response({'detail': f'Feature "{feature}" not available in Stage {user_stage}!'}, status=HTTP_403_FORBIDDEN)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
