from django.urls import path

from . import views

urlpatterns =[
    path('get_flight_details', views.get_flight_details),
    path('get_flights', views.get_flights),
    path('booking_flight', views.booking_flight),
    path('cancel_booking', views.cancel_booking),
    path('alter_seat', views.alter_seat),
]