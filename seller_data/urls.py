from django.urls import path
import seller_data.views as views

urlpatterns = [
    path('view-seller/<int:seller_id>', views.seller_data, name='seller_model_data'),
    path('update-seller/<int:seller_id>', views.update_seller_data, name='update_seller_data'),
    path('add-seller', views.add_seller, name='add_seller'),
    path('delete-seller/<int:seller_id>', views.delete_seller, name='delete_seller')
]
