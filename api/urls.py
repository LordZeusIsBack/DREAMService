from django.urls import path
import api.views as views

urlpatterns = [
    path('view-seller-model', views.seller_model_data, name='seller_model'),
]