from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={"required": "El correo electrónico es obligatorio."},
        widget=forms.EmailInput(attrs={
            "placeholder": "correo@ejemplo.com"
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        error_messages = {
            'password_mismatch': "Las contraseñas no coinciden.",
        }
        error_messages = {
            'username': {
                'required': "El nombre de usuario es obligatorio.",
                'unique': "Este nombre de usuario ya está en uso.",
            },
            'password1': {
                'required': "La contraseña es obligatoria.",
            },
            'password2': {
                'required': "Debés confirmar la contraseña.",
                'password_mismatch': "Las contraseñas no coinciden.",
            },
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def __init__(self, *args, **kwargs):
        super(RegistroForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w-full border p-2 rounded focus:ring-2 focus:ring-green-400'
