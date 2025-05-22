from django.urls import path
from .views import index, contacto # Asegúrate de importar la vista

urlpatterns = [
    path('', index, name='home'),
    path('contacto/', contacto, name='contacto')
     # Define la ruta para 'about'
]

