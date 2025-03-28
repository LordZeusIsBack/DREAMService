from django.urls import path
import api.views as views

urlpatterns = [
    path('index-checking', views.index, name='index'),
]