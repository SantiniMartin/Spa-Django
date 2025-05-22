from django import forms
from .models import Contacto  # Importa el modelo que creaste en models.py

class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'correo', 'mensaje']