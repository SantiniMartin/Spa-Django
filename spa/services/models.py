from django.db import models
from django.contrib.auth.models import User

class Professional(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(default=60)
    max_people = models.PositiveIntegerField(null=True, blank=True)  # None si es individual
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def is_collective(self):
        return self.max_people is not None

    def is_collective(self):
        return self.max_people is not None

class Schedule(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=[(i, day) for i, day in enumerate(['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'])])
    start_time = models.TimeField()
    end_time = models.TimeField()


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('service', 'date', 'time', 'user')

