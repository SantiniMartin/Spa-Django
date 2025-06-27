from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now, make_aware
from datetime import timedelta, datetime
from django.contrib import messages
from django.db.models import Sum

from .models import Service, Schedule, Appointment
from cart.models import CartItem, Cart, PagoItem

def lista_servicios(request):
    servicios = Service.objects.all()
    return render(request, 'services/lista_servicios.html', {'servicios': servicios})

#@login_required
def detalle_servicio(request, service_id):
    servicio = get_object_or_404(Service, id=service_id)
    fecha_min = now().date() + timedelta(days=1)
    horas_disponibles = []
    mensaje_error = None

    fecha_str = request.GET.get('fecha')
    fecha = None

    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha = None

    if fecha and fecha >= fecha_min:
        # Validar que la fecha esté al menos 48 horas en el futuro
        ahora = now()
        fecha_hora_minima = ahora + timedelta(hours=48)
        
        if fecha < fecha_hora_minima.date():
            mensaje_error = "Las reservas deben realizarse con al menos 48 horas de anticipación."
        else:
            dia_semana = fecha.weekday()
            horarios = Schedule.objects.filter(service=servicio, day_of_week=dia_semana)

            for horario in horarios:
                hora_actual = datetime.combine(fecha, horario.start_time)
                hora_fin = datetime.combine(fecha, horario.end_time)

                while hora_actual < hora_fin:
                    hora = hora_actual.time()
                    # Hacer aware el datetime
                    fecha_hora_servicio = make_aware(datetime.combine(fecha, hora))
                    if fecha_hora_servicio <= ahora + timedelta(hours=48):
                        hora_actual += timedelta(minutes=servicio.duration_minutes)
                        continue

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
        'mensaje_error': mensaje_error,
    })

@login_required
def reservar_turno(request, service_id):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.method == 'POST':
            try:
                print(f"DEBUG: Iniciando reserva para servicio ID: {service_id}")
                servicio = get_object_or_404(Service, id=service_id)
                print(f"DEBUG: Servicio encontrado: {servicio.name}")
                
                fecha_str = request.POST.get('date')
                hora_str = request.POST.get('time')
                print(f"DEBUG: Fecha recibida: {fecha_str}, Hora recibida: {hora_str}")

                if not fecha_str or not hora_str:
                    print("DEBUG: Fecha u hora faltante")
                    return redirect('detalle_servicio', service_id=service_id)

                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    hora = datetime.strptime(hora_str, "%H:%M").time()
                    print(f"DEBUG: Fecha parseada: {fecha}, Hora parseada: {hora}")
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Error parseando fecha/hora: {e}")
                    return redirect('detalle_servicio', service_id=service_id)

                if fecha <= now().date():
                    print("DEBUG: Fecha en el pasado")
                    return redirect('detalle_servicio', service_id=service_id)

                # Validar que la reserva sea al menos 48 horas antes
                ahora = now()
                fecha_hora_servicio = make_aware(datetime.combine(fecha, hora))
                tiempo_restante = fecha_hora_servicio - ahora
                
                if tiempo_restante < timedelta(hours=48):
                    print(f"DEBUG: Reserva muy próxima. Tiempo restante: {tiempo_restante}")
                    # Redirigir con mensaje de error
                    return redirect('detalle_servicio', service_id=service_id)

                dia_semana = fecha.weekday()
                horarios = Schedule.objects.filter(service=servicio, day_of_week=dia_semana)
                dentro_del_horario = any(h.start_time <= hora < h.end_time for h in horarios)
                print(f"DEBUG: Día semana: {dia_semana}, Horarios encontrados: {horarios.count()}, Dentro del horario: {dentro_del_horario}")
                
                if not dentro_del_horario:
                    print("DEBUG: Fuera del horario disponible")
                    return redirect('detalle_servicio', service_id=service_id)

                if servicio.max_people:
                    cantidad = Appointment.objects.filter(service=servicio, date=fecha, time=hora).count()
                    print(f"DEBUG: Servicio colectivo, reservas actuales: {cantidad}/{servicio.max_people}")
                    if cantidad >= servicio.max_people:
                        print("DEBUG: Servicio lleno")
                        return redirect('detalle_servicio', service_id=service_id)
                else:
                    existe_reserva = Appointment.objects.filter(service=servicio, date=fecha, time=hora).exists()
                    print(f"DEBUG: Servicio individual, reserva existente: {existe_reserva}")
                    if existe_reserva:
                        print("DEBUG: Ya hay una reserva para este horario")
                        return redirect('detalle_servicio', service_id=service_id)

                # Crear la cita
                print("DEBUG: Creando cita...")
                Appointment.objects.create(
                    user=request.user,
                    service=servicio,
                    date=fecha,
                    time=hora
                )
                print("DEBUG: Cita creada exitosamente")
                
                # Verificar y crear carrito si no existe
                try:
                    cart = request.user.cart
                    print(f"DEBUG: Carrito existente encontrado: {cart.id}")
                except Exception as e:
                    print(f"DEBUG: Error accediendo al carrito: {e}")
                    cart, created = Cart.objects.get_or_create(user=request.user)
                    print(f"DEBUG: Carrito creado: {created}, ID: {cart.id}")
                
                # Agregar el servicio al carrito
                print("DEBUG: Agregando servicio al carrito...")
                item, created = CartItem.objects.get_or_create(cart=cart, service=servicio)
                if not created:
                    item.cantidad += 1
                    item.save()
                    print(f"DEBUG: Cantidad actualizada: {item.cantidad}")
                else:
                    print("DEBUG: Nuevo item creado en carrito")
                
                print("DEBUG: Redirigiendo a confirmación...")
                return redirect('confirmacion_turno')
                
            except Exception as e:
                # Log del error para debugging
                print(f"ERROR en reservar_turno: {e}")
                import traceback
                traceback.print_exc()
                return redirect('detalle_servicio', service_id=service_id)

        return redirect('lista_servicios')


@login_required
def confirmacion_turno(request):
    return render(request, 'services/confirmacion.html')

@login_required
def mis_citas(request):
    citas = Appointment.objects.filter(user=request.user).order_by('date', 'time')
    return render(request, 'services/mis_citas.html', {'citas': citas})

@login_required
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Appointment, id=cita_id, user=request.user)
    cita.delete()
    messages.success(request, "Cita cancelada correctamente. El horario ya está disponible para otros usuarios.")
    return redirect('mis_citas')

@login_required
def modificar_cita(request, cita_id):
    cita = get_object_or_404(Appointment, id=cita_id, user=request.user)
    from .models import Service, Schedule
    servicios = Service.objects.all()
    selected_service_id = request.POST.get('servicio') or cita.service.id
    selected_service = Service.objects.get(id=selected_service_id)
    selected_fecha = request.POST.get('fecha') or cita.date
    horas_disponibles = []
    if selected_fecha:
        import datetime
        fecha_dt = selected_fecha if isinstance(selected_fecha, datetime.date) else datetime.datetime.strptime(selected_fecha, "%Y-%m-%d").date()
        dia_semana = fecha_dt.weekday()
        horarios = Schedule.objects.filter(service=selected_service, day_of_week=dia_semana)
        for horario in horarios:
            hora_actual = datetime.datetime.combine(fecha_dt, horario.start_time)
            hora_fin = datetime.datetime.combine(fecha_dt, horario.end_time)
            while hora_actual < hora_fin:
                hora = hora_actual.time()
                if not Appointment.objects.filter(service=selected_service, date=fecha_dt, time=hora).exclude(id=cita.id).exists():
                    horas_disponibles.append(hora)
                hora_actual += datetime.timedelta(minutes=selected_service.duration_minutes)
    if request.method == 'POST' and request.POST.get('fecha') and request.POST.get('hora') and request.POST.get('servicio'):
        cita.service = selected_service
        cita.date = selected_fecha
        cita.time = request.POST.get('hora')
        cita.save()
        messages.success(request, 'Cita modificada correctamente.')
        return redirect('mis_citas')
    return render(request, 'services/modificar_cita.html', {
        'cita': cita,
        'servicios': servicios,
        'selected_service': selected_service,
        'selected_fecha': selected_fecha,
        'horas_disponibles': horas_disponibles,
    })

@user_passes_test(lambda u: u.is_superuser or u.username in ['dra_felicidad', 'martin'])
def reporte_totales_servicio(request):
    from django.db.models import Sum
    from datetime import datetime
    from cart.models import PagoItem
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    items = []
    if fecha_inicio and fecha_fin:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        items = PagoItem.objects.filter(
            pago__fecha__date__gte=fecha_inicio_dt,
            pago__fecha__date__lte=fecha_fin_dt
        ).select_related('pago', 'service', 'pago__user')
    return render(request, 'services/reporte_totales_servicio.html', {
        'items': items,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })

