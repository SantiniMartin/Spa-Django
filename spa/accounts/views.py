from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils.timezone import now
from datetime import timedelta
from services.models import Appointment
from collections import defaultdict
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os
from services.models import Appointment 
from accounts.utils import es_admin 


def es_profesional(user):
    return user.groups.filter(name='Profesional').exists()

@login_required
@user_passes_test(es_profesional)
def panel_profesional(request):
    manana = now().date() + timedelta(days=1)
    turnos = Appointment.objects.filter(
        service__professional__user=request.user,
        date=manana
    ).order_by('time')

    return render(request, 'accounts/panel_profesional.html', {
        'turnos': turnos,
        'fecha': manana
    })
    
def es_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(es_admin)
def panel_admin(request):
    from datetime import datetime
    from collections import defaultdict

    fecha_str = request.GET.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else now().date()
    except ValueError:
        fecha = now().date()

    turnos = Appointment.objects.select_related('service', 'user') \
        .filter(date=fecha).order_by('service__name', 'time')

    turnos_por_servicio = defaultdict(list)
    for turno in turnos:
        turnos_por_servicio[turno.service.name].append(turno)

    return render(request, 'accounts/panel_admin.html', {
        'turnos_por_servicio': dict(turnos_por_servicio),
        'fecha': fecha,
    })


#Imprimir en PDF
@login_required
@user_passes_test(es_admin)
def exportar_pdf_agenda(request):
    from datetime import datetime

    fecha_str = request.GET.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else now().date()
    except ValueError:
        fecha = now().date()

    turnos = Appointment.objects.select_related('service', 'user') \
        .filter(date=fecha).order_by('service__name', 'time')

    turnos_por_servicio = defaultdict(list)
    for turno in turnos:
        turnos_por_servicio[turno.service.name].append(turno)

    template = get_template('accounts/agenda_pdf.html')
    html = template.render({
        'turnos_por_servicio': turnos_por_servicio,
        'fecha': fecha,
        'logo_path': os.path.join(settings.MEDIA_ROOT, 'spa', 'place_holder.png'),
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="agenda_{fecha}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response
