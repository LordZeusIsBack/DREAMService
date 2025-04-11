from django.urls import path
import buyer_data.views as views

urlpatterns = [
    path('view-buyer-data', views.view_buyer_model, name='view_buyer_model'),
    path('view-buyer/<str:buyer_username>', views.buyer_data, name='view_buyer'),
    path('update-buyer/<str:buyer_username>', views.update_buyer_data, name='update_buyer'),
]
