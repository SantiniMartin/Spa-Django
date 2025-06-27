from django.urls import path
#from .views import panel_profesional
from .views import panel_profesional, panel_admin
from .views import exportar_pdf_agenda, exportar_pdf_profesional

urlpatterns = [
    path('profesional/panel/', panel_profesional, name='panel_profesional'),
    path('profesional/panel/pdf/', exportar_pdf_profesional, name='exportar_pdf_profesional'),
    path('admin/panel/', panel_admin, name='panel_admin'),
    path('admin/panel/pdf/', exportar_pdf_agenda, name='exportar_pdf_agenda'),
]