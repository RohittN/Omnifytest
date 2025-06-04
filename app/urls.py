from django.urls import path
from . import views

urlpatterns = [
    path('classes/', views.get_classes, name='get_classes'),
    path('book/', views.book_class, name='book_class'),
    path('bookings/', views.get_bookings, name='get_bookings'),
]