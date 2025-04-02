from django.urls import path
import api.views as views

urlpatterns = [
    path('view-seller/<int:seller_id>', views.seller_model_data, name='seller_model_data'),
]