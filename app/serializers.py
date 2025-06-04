from rest_framework import serializers
from .models import FitnessClass, Booking
from django.utils import timezone

class FitnessClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessClass
        fields = ['id', 'name', 'class_type', 'datetime', 'instructor', 'available_slots']

class BookingCreateSerializer(serializers.ModelSerializer):
    class_id = serializers.IntegerField()
    
    class Meta:
        model = Booking
        fields = ['class_id', 'client_name', 'client_email']
    
    def validate_class_id(self, value):
        try:
            fitness_class = FitnessClass.objects.get(id=value)
            if fitness_class.available_slots <= 0:
                raise serializers.ValidationError("No available slots for this class")
            if fitness_class.datetime < timezone.now():
                raise serializers.ValidationError("Cannot book past classes")
            return value
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Class does not exist")

class BookingSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='fitness_class.name', read_only=True)
    class_datetime = serializers.DateTimeField(source='fitness_class.datetime', read_only=True)
    instructor = serializers.CharField(source='fitness_class.instructor', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'class_name', 'class_datetime', 'instructor', 'client_name', 'booking_time']