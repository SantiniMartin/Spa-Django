from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_servicios, name='lista_servicios'),
    path('<int:service_id>/', views.detalle_servicio, name='detalle_servicio'),
    path('<int:service_id>/reservar/', views.reservar_turno, name='reservar_turno'),
    path('confirmacion/', views.confirmacion_turno, name='confirmacion_turno'),
    path('mis-citas/', views.mis_citas, name='mis_citas'),

]
