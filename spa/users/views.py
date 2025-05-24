# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('/')
    else:
        form = RegistroForm()
    return render(request, 'users/register.html', {'form': form})

def home(request):
    return render(request, 'home.html')