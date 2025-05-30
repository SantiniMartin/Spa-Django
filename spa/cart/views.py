from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem
from store.models import Product
from django.contrib.auth.decorators import login_required

@login_required
def agregar_producto(request, producto_id):
    product = get_object_or_404(Product, id=producto_id)
    cart = request.user.cart
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.cantidad += 1
        item.save()
    return redirect('ver_carrito')
##
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
    return render(request, 'cart/checkout.html', {'carrito': request.user.cart})

@login_required
def confirmar_compra(request):
    request.user.cart.items.all().delete()
    return redirect('confirmacion')

@login_required
def confirmacion(request):
    return render(request, 'cart/confirmacion.html')
