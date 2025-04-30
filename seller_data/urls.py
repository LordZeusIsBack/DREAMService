import seller_data.views as views

urlpatterns = [
    path('view-seller/<str:seller_username>', views.seller_data, name='view_seller'),
    path('update-seller/<str:seller_username>', views.update_seller_data, name='update_seller'),
    path('add-seller', views.add_seller, name='add_seller'),
    path('delete-seller/<str:seller_username>', views.delete_seller, name='delete_seller'),
    path('forgot-password/', views.seller_forgot_password, name='seller_forgot_password'),
    path('reset-password/', views.seller_reset_password, name='seller_reset_password'),
    path('login/', views.seller_login, name='seller_login'),
]
