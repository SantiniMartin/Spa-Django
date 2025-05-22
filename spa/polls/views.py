from django.http import HttpResponse
from django.shortcuts import render,redirect
from .forms import ContactoForm


#def index(request):
 #   return HttpResponse("Hello agarrini la palini. You're at the polls index.")



def index(request):
   return render(request, 'polls/index.html')
  # Asegura que el nombre sea correcto



def contacto(request):
    if request.method == 'POST':  # Si el formulario se envía
        form = ContactoForm(request.POST)
        if form.is_valid():  # Validamos los datos
            form.save()  # Guardamos en la base de datos
            return redirect('index')  # Redirigir a la página principal después de enviar
    else:  # Si es una petición GET, mostrar el formulario vacío
        form = ContactoForm()
    return render(request, 'polls/contacto.html', {'form': form})
