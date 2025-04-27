from django.urls import path, include
from estate_data import views
urlpatterns = [
    path('estate-details/<str:estate_slug>', views.get_estate_data),
    path('add-new-estate', views.add_new_estate),
]