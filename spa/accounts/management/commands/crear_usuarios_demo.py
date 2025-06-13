from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Crea usuarios de ejemplo para Cliente, Profesional y Dra. Felicidad'

    def handle(self, *args, **options):
        # Cliente
        cliente, _ = User.objects.get_or_create(username='cliente_demo')
        cliente.set_password('cliente123')
        cliente.email = 'cliente@example.com'
        cliente.save()
        cliente.groups.set([Group.objects.get(name='Cliente')])
        
        # Profesional
        profesional, _ = User.objects.get_or_create(username='profesional_demo')
        profesional.set_password('profesional123')
        profesional.email = 'profesional@example.com'
        profesional.save()
        profesional.groups.set([Group.objects.get(name='Profesional')])
        
        # Dra. Felicidad
        dra, created = User.objects.get_or_create(username='dra_felicidad')
        dra.set_password('dra123')
        dra.email = 'dra@example.com'
        dra.is_staff = True
        dra.is_superuser = True
        dra.save()
