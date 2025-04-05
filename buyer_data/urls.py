from django.urls import path
import buyer_data.views as views

urlpatterns = [
    path('view-buyer-data', views.view_buyer_model, name='view_buyer_model'),
]
