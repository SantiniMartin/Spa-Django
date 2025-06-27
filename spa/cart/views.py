from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem, Pago, PagoItem
from services.models import Service
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from services.models import Appointment

@login_required
def agregar_servicio(request, servicio_id):
    service = get_object_or_404(Service, id=servicio_id)
    cart = request.user.cart
    item, created = CartItem.objects.get_or_create(cart=cart, service=service)
    if not created:
        item.cantidad += 1
        item.save()
    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    return render(request, 'cart/ver_carrito.html', {'carrito': request.user.cart})

@login_required
def modificar_cantidad(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)
    nueva_cantidad = int(request.POST.get('cantidad', 1))
    if nueva_cantidad > 0:
        item.cantidad = nueva_cantidad
        item.save()
    else:
        item.delete()
    return redirect('ver_carrito')

@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)
    item.delete()
    return redirect('ver_carrito')

@login_required
def checkout(request):
    carrito = request.user.cart
    descuento = 0
    total_con_descuento = carrito.total_price()
    metodo_pago = request.POST.get('metodo_pago') if request.method == 'POST' else None
    aplica_descuento = False

    servicios_a_mas_de_48hs = True
    ahora = now()
    fechas_citas = set()
    for item in carrito.items.all():
        proxima_cita = item.service.appointment_set.filter(user=request.user).order_by('date', 'time').first()
        if proxima_cita:
            fecha_hora_servicio = make_aware(datetime.combine(proxima_cita.date, proxima_cita.time))
            if fecha_hora_servicio - ahora < timedelta(hours=48):
                servicios_a_mas_de_48hs = False
            fechas_citas.add(proxima_cita.date)

    pago_conjunto_habilitado = len(fechas_citas) == 1 and len(fechas_citas) > 0

    if metodo_pago == 'debito' and servicios_a_mas_de_48hs:
        aplica_descuento = True
        descuento = round(carrito.total_price() * Decimal('0.15'), 2)
        total_con_descuento = round(carrito.total_price() - descuento, 2)

    return render(request, 'cart/checkout.html', {
        'carrito': carrito,
        'descuento': descuento,
        'total_con_descuento': total_con_descuento,
        'aplica_descuento': aplica_descuento,
        'metodo_pago': metodo_pago,
        'pago_conjunto_habilitado': pago_conjunto_habilitado,
        'fechas_citas': fechas_citas,
    })

@login_required
def confirmar_compra(request):
    carrito = request.user.cart
    metodo_pago = request.POST.get('metodo_pago')
    descuento = 0
    total_con_descuento = carrito.total_price()
    aplica_descuento = False

    servicios_a_mas_de_48hs = True
    ahora = now()
    for item in carrito.items.all():
        proxima_cita = item.service.appointment_set.filter(user=request.user).order_by('date', 'time').first()
        if proxima_cita:
            fecha_hora_servicio = make_aware(datetime.combine(proxima_cita.date, proxima_cita.time))
            if fecha_hora_servicio - ahora < timedelta(hours=48):
                servicios_a_mas_de_48hs = False
                break

    if metodo_pago == 'debito' and servicios_a_mas_de_48hs:
        aplica_descuento = True
        descuento = round(carrito.total_price() * Decimal('0.15'), 2)
        total_con_descuento = round(carrito.total_price() - descuento, 2)

    servicios = []
    for item in carrito.items.all():
        cita = Appointment.objects.filter(user=request.user, service=item.service).order_by('-created_at').first()
        servicios.append({
            'nombre': item.service.name,
            'cantidad': item.cantidad,
            'subtotal': item.total_price(),
            'service_obj': item.service,
            'fecha_cita': cita.date if cita else None,
            'hora_cita': cita.time if cita else None,
        })

    pago = Pago.objects.create(
        user=request.user,
        total=total_con_descuento if aplica_descuento else carrito.total_price(),
        metodo_pago=metodo_pago or ''
    )
    for s in servicios:
        PagoItem.objects.create(
            pago=pago,
            service=s['service_obj'],
            cantidad=s['cantidad'],
            subtotal=s['subtotal'],
            fecha_cita=s['fecha_cita'],
            hora_cita=s['hora_cita']
        )

    context = {
        'usuario': request.user,
        'servicios': servicios,
        'aplica_descuento': aplica_descuento,
        'descuento': descuento,
        'total_pagado': total_con_descuento if aplica_descuento else carrito.total_price(),
        'metodo_pago': metodo_pago,
    }
    html_content = render_to_string('cart/comprobante_pago_email.html', context)
    subject = 'Comprobante de pago - Spa'
    to_email = [request.user.email]
    email = EmailMessage(subject, html_content, to=to_email)
    email.content_subtype = 'html'
    email.send()
    messages.success(request, "Correo enviado correctamente")
    carrito.items.all().delete()
    return render(request, 'cart/confirmacion.html', context)

@login_required
def confirmacion(request):
    return render(request, 'cart/confirmacion.html')

@login_required
def eliminar_item_checkout(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)
    item.delete()
    return redirect('checkout')
