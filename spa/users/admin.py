from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from services.models import Appointment

def setup_roles():
    # Grupo: Profesional
    prof_group, _ = Group.objects.get_or_create(name='Profesional')
    # Ejemplo: permitir ver turnos (puedes agregar más)
    content_type = ContentType.objects.get_for_model(Appointment)
    permiso = Permission.objects.get(content_type=content_type, codename='view_appointment')
    prof_group.permissions.add(permiso)

    # Grupo: Cliente (opcional si querés filtrar después)
    Group.objects.get_or_create(name='Cliente')
