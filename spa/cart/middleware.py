#habia sido que necesita comenzar con un carrito
from .models import Cart

class EnsureCartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            Cart.objects.get_or_create(user=request.user)
        return self.get_response(request)
