from django.urls import path, include
from estate_data import views
urlpatterns = [
    path('estate-details/<str:estate_slug>', views.get_estate_data, name='estate_details'),
    path('add-new-estate', views.add_new_estate, name='add_new_estate'),
    path('update-estate/<str:slug>', views.update_estate_data, name='update_estate_data'),
]