from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils.timezone import now
from datetime import timedelta, datetime
from services.models import Appointment
from collections import defaultdict
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
import os
from xhtml2pdf import pisa
from accounts.utils import es_admin 


def es_profesional(user):
    return user.groups.filter(name='Profesional').exists()

@login_required
@user_passes_test(es_profesional)
def panel_profesional(request):
    fecha_str = request.GET.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else now().date()
    except ValueError:
        fecha = now().date()

    # Obtener turnos del profesional para la fecha seleccionada
    turnos = Appointment.objects.select_related('service', 'user') \
        .filter(
            service__professional__user=request.user,
            date=fecha,
            user__isnull=False,  # Solo turnos con usuario válido
            service__isnull=False  # Solo turnos con servicio válido
        ).order_by('time')

    # Agrupar turnos por servicio
    turnos_por_servicio = defaultdict(list)
    for turno in turnos:
        # Verificar que el turno tenga todos los datos necesarios
        if turno.user and turno.service:
            turnos_por_servicio[turno.service.name].append(turno)

    # Estadísticas
    total_turnos = turnos.count()
    servicios_con_turnos = len(turnos_por_servicio)

    return render(request, 'accounts/panel_profesional.html', {
        'turnos_por_servicio': dict(turnos_por_servicio),
        'turnos': turnos,  # Mantener compatibilidad con plantilla actual
        'fecha': fecha,
        'total_turnos': total_turnos,
        'servicios_con_turnos': servicios_con_turnos,
    })
    
def es_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(es_admin)
def panel_admin(request):
    fecha_str = request.GET.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else now().date()
    except ValueError:
        fecha = now().date()

    # Obtener todos los turnos del día seleccionado con datos válidos
    turnos = Appointment.objects.select_related('service', 'user', 'service__professional') \
        .filter(
            date=fecha,
            user__isnull=False,  # Solo turnos con usuario válido
            service__isnull=False  # Solo turnos con servicio válido
        ).order_by('service__name', 'time')

    # Agrupar turnos por servicio
    turnos_por_servicio = defaultdict(list)
    for turno in turnos:
        # Verificar que el turno tenga todos los datos necesarios
        if turno.user and turno.service:
            turnos_por_servicio[turno.service.name].append(turno)

    # Estadísticas
    total_turnos = turnos.count()
    servicios_con_turnos = len(turnos_por_servicio)

    return render(request, 'accounts/panel_admin.html', {
        'turnos_por_servicio': dict(turnos_por_servicio),
        'fecha': fecha,
        'total_turnos': total_turnos,
        'servicios_con_turnos': servicios_con_turnos,
    })


@login_required
@user_passes_test(es_admin)
def exportar_pdf_agenda(request):
    try:
        fecha_str = request.GET.get('fecha')
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else now().date()
        except ValueError:
            fecha = now().date()

        # Obtener todos los turnos del día seleccionado con datos válidos
        turnos = Appointment.objects.select_related('service', 'user', 'service__professional') \
            .filter(
                date=fecha,
                user__isnull=False,  # Solo turnos con usuario válido
                service__isnull=False  # Solo turnos con servicio válido
            ).order_by('service__name', 'time')

        # Agrupar turnos por servicio
        turnos_por_servicio = defaultdict(list)
        for turno in turnos:
            # Verificar que el turno tenga todos los datos necesarios
            if turno.user and turno.service:
                turnos_por_servicio[turno.service.name].append(turno)

        # Estadísticas para el PDF
        total_turnos = turnos.count()
        servicios_con_turnos = len(turnos_por_servicio)

        # Ruta del logo
        logo_path = os.path.join(settings.MEDIA_ROOT, 'spa', 'place_holder.png')
        if not os.path.exists(logo_path):
            logo_path = None

        # Intentar usar la plantilla principal primero
        try:
            template = get_template('accounts/agenda_pdf.html')
        except:
            # Si falla, usar la plantilla simplificada
            template = get_template('accounts/agenda_pdf_simple.html')

        html = template.render({
            'turnos_por_servicio': dict(turnos_por_servicio),
            'fecha': fecha,
            'logo_path': logo_path,
            'total_turnos': total_turnos,
            'servicios_con_turnos': servicios_con_turnos,
        })

        # Crear respuesta PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="agenda_{fecha}.pdf"'
        
        # Generar PDF con manejo de errores
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            # Si hay error en la generación del PDF, devolver un mensaje de error
            return HttpResponse(
                f'Error al generar PDF: {pisa_status.err}',
                content_type='text/plain',
                status=500
            )
        
        return response
        
    except Exception as e:
        # Manejar cualquier otro error
        return HttpResponse(
            f'Error inesperado: {str(e)}',
            content_type='text/plain',
            status=500
        )

@login_required
@user_passes_test(es_profesional)
def exportar_pdf_profesional(request):
    try:
        fecha_str = request.GET.get('fecha')
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else now().date()
        except ValueError:
            fecha = now().date()

        # Obtener turnos del profesional para la fecha seleccionada
        turnos = Appointment.objects.select_related('service', 'user') \
            .filter(
                service__professional__user=request.user,
                date=fecha,
                user__isnull=False,  # Solo turnos con usuario válido
                service__isnull=False  # Solo turnos con servicio válido
            ).order_by('time')

        # Agrupar turnos por servicio
        turnos_por_servicio = defaultdict(list)
        for turno in turnos:
            # Verificar que el turno tenga todos los datos necesarios
            if turno.user and turno.service:
                turnos_por_servicio[turno.service.name].append(turno)

        # Estadísticas para el PDF
        total_turnos = turnos.count()
        servicios_con_turnos = len(turnos_por_servicio)

        # Ruta del logo
        logo_path = os.path.join(settings.MEDIA_ROOT, 'spa', 'place_holder.png')
        if not os.path.exists(logo_path):
            logo_path = None

        # Usar plantilla simplificada para profesionales
        template = get_template('accounts/agenda_pdf_simple.html')

        html = template.render({
            'turnos_por_servicio': dict(turnos_por_servicio),
            'fecha': fecha,
            'logo_path': logo_path,
            'total_turnos': total_turnos,
            'servicios_con_turnos': servicios_con_turnos,
        })

        # Crear respuesta PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="mis_turnos_{fecha}.pdf"'
        
        # Generar PDF con manejo de errores
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            # Si hay error en la generación del PDF, devolver un mensaje de error
            return HttpResponse(
                f'Error al generar PDF: {pisa_status.err}',
                content_type='text/plain',
                status=500
            )
        
        return response
        
    except Exception as e:
        # Manejar cualquier otro error
        return HttpResponse(
            f'Error inesperado: {str(e)}',
            content_type='text/plain',
            status=500
        )
