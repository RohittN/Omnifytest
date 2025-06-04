from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import FitnessClass

class Command(BaseCommand):
    help = 'Load sample fitness classes data'

    def handle(self, *args, **options):
        # Clear existing data
        FitnessClass.objects.all().delete()
        
        # Get current time in IST
        now = timezone.now()
        
        # Sample classes data
        classes_data = [
            {
                'name': 'Morning Yoga Flow',
                'class_type': 'yoga',
                'datetime': now + timedelta(days=1, hours=8),  # Tomorrow 8 AM
                'instructor': 'Priya Sharma',
                'total_slots': 15,
                'available_slots': 15,
            },
            {
                'name': 'Power HIIT Session',
                'class_type': 'hiit',
                'datetime': now + timedelta(days=1, hours=18),  # Tomorrow 6 PM
                'instructor': 'Rahul Singh',
                'total_slots': 12,
                'available_slots': 12,
            },
            {
                'name': 'Zumba Dance Party',
                'class_type': 'zumba',
                'datetime': now + timedelta(days=2, hours=17),  # Day after tomorrow 5 PM
                'instructor': 'Maria Rodriguez',
                'total_slots': 20,
                'available_slots': 20,
            },
            {
                'name': 'Evening Relaxing Yoga',
                'class_type': 'yoga',
                'datetime': now + timedelta(days=3, hours=19),  # 3 days from now 7 PM
                'instructor': 'Anjali Gupta',
                'total_slots': 10,
                'available_slots': 8,  # Some slots already booked
            },
            {
                'name': 'High Intensity HIIT',
                'class_type': 'hiit',
                'datetime': now + timedelta(days=4, hours=6),  # 4 days from now 6 AM
                'instructor': 'Vikram Kumar',
                'total_slots': 15,
                'available_slots': 15,
            }
        ]
        
        # Create fitness classes
        for class_data in classes_data:
            fitness_class = FitnessClass.objects.create(**class_data)
            self.stdout.write(
                self.style.SUCCESS(f'Created class: {fitness_class.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(classes_data)} fitness classes!')
        )