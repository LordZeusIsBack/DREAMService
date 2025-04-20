from django.urls import path, include

urlpatterns = [
    path('seller/', include('seller_data.urls')),
    path('buyer/', include('buyer_data.urls')),
    path('estate/', include('estate_data.urls'))
]