#habia sido que necesita comenzar con un carrito
from .models import Cart

class EnsureCartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                cart, created = Cart.objects.get_or_create(user=request.user)
                if created:
                    print(f"Carrito creado para usuario: {request.user.username}")
            except Exception as e:
                print(f"Error creando carrito para usuario {request.user.username}: {e}")
        return self.get_response(request)
