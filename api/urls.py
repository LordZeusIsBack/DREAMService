from django.urls import path
import api.views as views

urlpatterns = [
    path('view-seller-model', views.seller_model_data, name='seller_model_data'),
    path('update-seller-model', views.seller_model_update, name='seller_model_update'),
    path('delete-seller-model', views.seller_model_delete, name='seller_model_delete'),
]