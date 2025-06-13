from django.contrib.auth.decorators import login_required, user_passes_test

def es_profesional(user):
    return user.groups.filter(name='Profesional').exists()

@login_required
@user_passes_test(es_profesional)
def panel_profesional(request):
    # Turnos del día siguiente
    from datetime import timedelta
    from django.utils.timezone import now
    maniana = now().date() + timedelta(days=1)
    turnos = Appointment.objects.filter(service__professional__user=request.user, date=maniana)
    return render(request, 'services/panel_profesional.html', {'turnos': turnos})
