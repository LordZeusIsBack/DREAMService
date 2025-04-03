from django.urls import path
import api.views as views

urlpatterns = [
    path('view-seller/<int:seller_id>', views.seller_model_data, name='seller_model_data'),
    path('view-seller-data', views.model_data, name='seller_model_data'),
    path('update-seller/<int:seller_id>', views.update_seller_model_data, name='seller_model_data_update'),
    path('add-seller', views.add_new_user, name='add_seller'),
]