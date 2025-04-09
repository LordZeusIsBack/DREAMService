from django.urls import path
import seller_data.views as views

urlpatterns = [
    path('view-seller/<str:seller_email>', views.seller_data, name='seller_model_data'),
    path('update-seller/<str:seller_email>', views.update_seller_data, name='update_seller_data'),
    path('add-seller', views.add_seller, name='add_seller'),
    path('delete-seller/<str:seller_email>', views.delete_seller, name='delete_seller')
]
