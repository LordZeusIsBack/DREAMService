import buyer_data.views as views

urlpatterns = [
    path('view-buyer/<str:buyer_username>', views.buyer_data, name='view_buyer'),
    path('update-buyer/<str:buyer_username>', views.update_buyer_data, name='update_buyer'),
    path('add-buyer', views.add_buyer, name='add_buyer'),
    path('delete-buyer/<str:buyer_username>', views.delete_buyer, name='delete_buyer'),
    path('forgot-password/', views.buyer_forgot_password, name='buyer_forgot_password'),
    path('reset-password/', views.buyer_reset_password, name='buyer_reset_password'),
    path('buyer-login/', views.buyer_login, name='buyer_login'),
]
