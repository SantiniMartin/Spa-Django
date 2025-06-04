from django.urls import path
from . import views

urlpatterns = [
    path('service/', views.service, name='service'),
]