from django.contrib import admin
from .models import Service, Professional, Schedule, Appointment

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'professional', 'duration_minutes', 'max_people')

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('service', 'day_of_week', 'start_time', 'end_time')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'date', 'time')