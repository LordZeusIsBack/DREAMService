from django.urls import path
import seller_data.views as views

urlpatterns = [
    path('view-seller-data', views.model_data, name='seller_model_data')
]
