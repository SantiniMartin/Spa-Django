from django.db import models
from django.contrib.auth.models import User
from services.models import Service

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    fecha_reserva = models.DateField()
    cantidad = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.cantidad * self.service.rice
