from django.urls import path
import buyer_data.views as views
from common.urls import create_user_url_patterns

urlpatterns = create_user_url_patterns(views, 'buyer') + [
    path('eligibility-calculator', views.eligibility_calculator, name='eligibility_calculator'),
    path('emi-calculator', views.emi_calculator, name='emi_calculator'),
    path('affordability-calculator', views.affordability_calculator, name='affordability_calculator'),
    path('add-to-wishlist/<str:buyer_username>', views.add_bookmarks, name='add_bookmarks'),
    path('remove-bookmark/<str:buyer_username>', views.remove_bookmarks, name='remove_bookmarks'),
    path('get-bookmarks/<str:buyer_username>', views.bookmarked_estates, name='get_bookmarks'),
]
