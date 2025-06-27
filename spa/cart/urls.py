from django.urls import path
from . import views

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:servicio_id>/', views.agregar_servicio, name='agregar_servicio'),
    path('modificar/<int:item_id>/', views.modificar_cantidad, name='modificar_cantidad'),
    path('eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmar/', views.confirmar_compra, name='confirmar_compra'),
    path('confirmacion/', views.confirmacion, name='confirmacion'),
]
