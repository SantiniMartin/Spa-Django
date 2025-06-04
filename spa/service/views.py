
from django.shortcuts import render
from .models import Service

def service(request):
    #user = request.user
    services= Service.objects.all()
    #template = loader.get_template('appointment.html', {"user": user})
    return render(request, 'service.html',{"service":services})
