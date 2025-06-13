from django.shortcuts import render


# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import RegistroForm

def registro(request):
    next_url = request.GET.get('next', '/')  # Si no existe 'next', redirige a la home

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect(next_url)
    else:
        form = RegistroForm()
    return render(request, 'users/register.html', {'form': form})

def home(request):
    return render(request, 'home.html')