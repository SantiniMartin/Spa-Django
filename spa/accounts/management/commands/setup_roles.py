from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from services.models import Appointment

class Command(BaseCommand):
    help = 'Crea los grupos de usuarios y permisos por rol'

    def handle(self, *args, **kwargs):
        # Crear grupo Profesional
        profesional, _ = Group.objects.get_or_create(name='Profesional')
        content_type = ContentType.objects.get_for_model(Appointment)
        view_perm = Permission.objects.get(content_type=content_type, codename='view_appointment')
        profesional.permissions.add(view_perm)

        # Crear grupo Cliente
        Group.objects.get_or_create(name='Cliente')

        self.stdout.write(self.style.SUCCESS('✅ Grupos creados exitosamente'))
