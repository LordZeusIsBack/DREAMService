from django.urls import path
import seller_data.views as views
from common.urls import create_user_url_patterns

urlpatterns = create_user_url_patterns(views, 'seller') + [path('get_listed_estates/<str:seller_username>',
                                                               views.get_listed_estates, name='seller_estate_data')]
