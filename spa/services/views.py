from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta, datetime

from .models import Service, Schedule, Appointment

def lista_servicios(request):
    servicios = Service.objects.all()
    return render(request, 'services/lista_servicios.html', {'servicios': servicios})

#@login_required
def detalle_servicio(request, service_id):
    servicio = get_object_or_404(Service, id=service_id)
    fecha_min = now().date() + timedelta(days=1)
    horas_disponibles = []

    fecha_str = request.GET.get('fecha')
    fecha = None

    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha = None

    if fecha and fecha >= fecha_min:
        dia_semana = fecha.weekday()
        horarios = Schedule.objects.filter(service=servicio, day_of_week=dia_semana)

        for horario in horarios:
            hora_actual = datetime.combine(fecha, horario.start_time)
            hora_fin = datetime.combine(fecha, horario.end_time)

            while hora_actual < hora_fin:
                hora = hora_actual.time()

                if servicio.max_people:
                    reservas = Appointment.objects.filter(service=servicio, date=fecha, time=hora).count()
                    if reservas < servicio.max_people:
                        horas_disponibles.append(hora)
                else:
                    if not Appointment.objects.filter(service=servicio, date=fecha, time=hora).exists():
                        horas_disponibles.append(hora)

                hora_actual += timedelta(minutes=servicio.duration_minutes)

    return render(request, 'services/detalle_servicio.html', {
        'servicio': servicio,
        'fecha_min': fecha_min,
        'horas_disponibles': horas_disponibles,
    })

@login_required
def reservar_turno(request, service_id):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.method == 'POST':
            servicio = get_object_or_404(Service, id=service_id)
            fecha_str = request.POST.get('date')
            hora_str = request.POST.get('time')

            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                hora = datetime.strptime(hora_str, "%H:%M").time()
            except (ValueError, TypeError):
                return redirect('detalle_servicio', service_id=service_id)

            if fecha <= now().date():
                return redirect('detalle_servicio', service_id=service_id)

            dia_semana = fecha.weekday()
            horarios = Schedule.objects.filter(service=servicio, day_of_week=dia_semana)
            dentro_del_horario = any(h.start_time <= hora < h.end_time for h in horarios)
            if not dentro_del_horario:
                return redirect('detalle_servicio', service_id=service_id)

            if servicio.max_people:
                cantidad = Appointment.objects.filter(service=servicio, date=fecha, time=hora).count()
                if cantidad >= servicio.max_people:
                    return redirect('detalle_servicio', service_id=service_id)
            else:
                if Appointment.objects.filter(service=servicio, date=fecha, time=hora).exists():
                    return redirect('detalle_servicio', service_id=service_id)

            Appointment.objects.create(
                user=request.user,
                service=servicio,
                date=fecha,
                time=hora
            )
            return redirect('confirmacion_turno')

        return redirect('lista_servicios')


@login_required
def confirmacion_turno(request):
    return render(request, 'services/confirmacion.html')

from django.contrib.auth.decorators import login_required

@login_required
def mis_citas(request):
    citas = Appointment.objects.filter(user=request.user).order_by('date', 'time')
    return render(request, 'services/mis_citas.html', {'citas': citas})

