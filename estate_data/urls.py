from django.urls import path
from estate_data import views
from django.views.decorators.cache import cache_page
urlpatterns = [
    path('estate-details/<str:estate_slug>', views.get_estate_data, name='estate_details'),
    path('add-new-estate', views.add_new_estate, name='add_new_estate'),
    path('update-estate/<str:slug>', views.update_estate_data, name='update_estate_data'),
    path('area', cache_page(60*60)(views.EstateAreaView.as_view()), name='estate_area'),
]