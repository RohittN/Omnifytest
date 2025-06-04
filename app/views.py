from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingCreateSerializer, BookingSerializer
import logging
import pytz

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_classes(request):
    """
    GET /classes - Returns all upcoming fitness classes
    """
    try:
        # Get only future classes
        current_time = timezone.now()
        classes = FitnessClass.objects.filter(datetime__gt=current_time)
        serializer = FitnessClassSerializer(classes, many=True)
        
        logger.info(f"Retrieved {len(classes)} upcoming classes")
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(classes)
        })
    except Exception as e:
        logger.error(f"Error retrieving classes: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to retrieve classes'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_classes_by_timezone(request):
    """
    GET /classes/timezone?tz=US/Eastern - Returns classes converted to specified timezone
    Classes created in IST and on change of timezone all the slots should be changed accordingly
    """
    try:
        timezone_param = request.GET.get('tz', 'Asia/Kolkata')  # Default to IST
        
        try:
            target_timezone = pytz.timezone(timezone_param)
        except pytz.UnknownTimeZoneError:
            return Response({
                'success': False,
                'error': f'Invalid timezone: {timezone_param}. Please use valid timezone like US/Eastern, Asia/Tokyo, etc.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        current_time = timezone.now()
        classes = FitnessClass.objects.filter(datetime__gt=current_time)
        
        # Convert timezone for each class
        classes_data = []
        for cls in classes:
            # Convert datetime to target timezone
            converted_datetime = cls.datetime.astimezone(target_timezone)
            
            classes_data.append({
                'id': cls.id,
                'name': cls.name,
                'class_type': cls.class_type,
                'datetime': converted_datetime.isoformat(),
                'datetime_original_utc': cls.datetime.isoformat(),
                'timezone': str(target_timezone),
                'instructor': cls.instructor,
                'available_slots': cls.available_slots
            })
        
        logger.info(f"Retrieved {len(classes_data)} classes converted to {timezone_param}")
        return Response({
            'success': True,
            'data': classes_data,
            'count': len(classes_data),
            'requested_timezone': timezone_param
        })
        
    except Exception as e:
        logger.error(f"Error retrieving classes with timezone: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to retrieve classes'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def book_class(request):
    """
    POST /book - Book a fitness class
    Expected data: {"class_id": 1, "client_name": "John Doe", "client_email": "john@example.com"}
    """
    try:
        serializer = BookingCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                # Get the fitness class
                fitness_class = get_object_or_404(FitnessClass, id=serializer.validated_data['class_id'])
                
                # Check if user already booked this class
                existing_booking = Booking.objects.filter(
                    fitness_class=fitness_class,
                    client_email=serializer.validated_data['client_email']
                ).first()
                
                if existing_booking:
                    return Response({
                        'success': False,
                        'error': 'You have already booked this class'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check available slots again (double-check for race conditions)
                if fitness_class.available_slots <= 0:
                    return Response({
                        'success': False,
                        'error': 'No available slots for this class'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create booking
                booking = Booking.objects.create(
                    fitness_class=fitness_class,
                    client_name=serializer.validated_data['client_name'],
                    client_email=serializer.validated_data['client_email']
                )
                
                # Reduce available slots
                fitness_class.available_slots -= 1
                fitness_class.save()
                
                logger.info(f"Booking created for {booking.client_email} in class {fitness_class.name}")
                
                return Response({
                    'success': True,
                    'message': 'Booking successful',
                    'booking_id': booking.id,
                    'class_name': fitness_class.name,
                    'class_datetime': fitness_class.datetime
                }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to create booking'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_bookings(request):
    """
    GET /bookings?email=user@example.com - Get all bookings for a specific email
    """
    try:
        email = request.GET.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        bookings = Booking.objects.filter(client_email=email).select_related('fitness_class')
        serializer = BookingSerializer(bookings, many=True)
        
        logger.info(f"Retrieved {len(bookings)} bookings for email: {email}")
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(bookings)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving bookings: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to retrieve bookings'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def api_home(request):
    """
    API Home - List available endpoints
    """
    return Response({
        'message': 'Fitness Studio Booking API',
        'version': '1.0',
        'endpoints': {
            'GET /api/': 'API documentation',
            'GET /api/classes/': 'Get all upcoming fitness classes',
            'GET /api/classes/timezone/?tz=<timezone>': 'Get classes converted to specified timezone',
            'POST /api/book/': 'Book a fitness class',
            'GET /api/bookings/?email=<email>': 'Get bookings for an email'
        },
        'example_requests': {
            'book_class': {
                'method': 'POST',
                'url': '/api/book/',
                'body': {
                    'class_id': 1,
                    'client_name': 'John Doe',
                    'client_email': 'john@example.com'
                }
            },
            'timezone_conversion': {
                'method': 'GET',
                'url': '/api/classes/timezone/?tz=US/Eastern',
                'description': 'Convert class times to US Eastern timezone'
            }
        }
    })