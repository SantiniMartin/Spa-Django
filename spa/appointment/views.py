from django.shortcuts import render

def appointment(request):
    user = request.user
    #template = loader.get_template('appointment.html', {"user": user})
    return render(request, 'appointment.html',{"user": user})
