from django.urls import path
import seller_data.views as views

urlpatterns = [
    path('view-seller/<str:seller_username>', views.seller_data, name='seller_model_data'),
    path('update-seller/<str:seller_username>', views.update_seller_data, name='update_seller_data'),
    path('add-seller', views.add_seller, name='add_seller'),
    path('delete-seller/<str:seller_username>', views.delete_seller, name='delete_seller'),
    path('forgot-password/', views.forgot_password, name='forgot_seller_password'),
    path('reset-password/', views.reset_password, name='reset_seller_password'),
    path('login/', views.seller_login, name='seller_login'),
]
