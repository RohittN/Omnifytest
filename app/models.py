from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone
import pytz

class FitnessClass(models.Model):
    CLASS_TYPES = [
        ('yoga', 'Yoga'),
        ('zumba', 'Zumba'),
        ('hiit', 'HIIT'),
    ]
    
    name = models.CharField(max_length=100)
    class_type = models.CharField(max_length=20, choices=CLASS_TYPES)
    datetime = models.DateTimeField()
    instructor = models.CharField(max_length=100)
    total_slots = models.IntegerField(default=20)
    available_slots = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.datetime}"
    
    class Meta:
        ordering = ['datetime']

class Booking(models.Model):
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(validators=[EmailValidator()])
    booking_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client_name} - {self.fitness_class.name}"
    
    class Meta:
        unique_together = ['fitness_class', 'client_email'] 