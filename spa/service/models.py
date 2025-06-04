from django.db import models

# Create your models here.
class Service(models.Model):
    name_service= models.CharField(max_length=30, unique= True)
    description_service= models.CharField(max_length=150)
    price_service= models.DecimalField(max_digits=8, decimal_places=2)
    time_service= models.CharField(max_length=20)
    image_service= models.ImageField(upload_to='static/service/',blank=True, null=True)

    def __str__(self):
        return self.name_service
    


