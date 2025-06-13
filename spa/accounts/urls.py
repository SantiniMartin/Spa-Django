from django.urls import path
#from .views import panel_profesional
from .views import panel_profesional, panel_admin
from .views import exportar_pdf_agenda

urlpatterns = [
    path('profesional/panel/', panel_profesional, name='panel_profesional'),
    path('admin/panel/', panel_admin, name='panel_admin'),
    path('admin/panel/pdf/', exportar_pdf_agenda, name='exportar_pdf_agenda'),
]