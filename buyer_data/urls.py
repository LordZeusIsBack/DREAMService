from django.urls import path
import buyer_data.views as views
from common.urls import create_user_url_patterns

urlpatterns = create_user_url_patterns(views, 'buyer') + [
    path('affordability-calculator', views.affordability_calculator, name='affordability_calculator')
]
