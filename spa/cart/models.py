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
    cantidad = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.cantidad * self.service.rice

# --- NUEVO: Registro de pagos ---
class Pago(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20)

class PagoItem(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_cita = models.DateField(null=True, blank=True)
    hora_cita = models.TimeField(null=True, blank=True)
