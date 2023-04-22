from django.urls import path

from . import views

urlpatterns =[
    path("", views.index, name="flights"),
    path("search_flight", views.list_flights, name="search_flight"),
    path("<int:flight_id>", views.flight, name="flight"),
    path("get_flight_details", views.get_flight_details, name="get_flight_details"),
    path("booking_flight", views.book, name="booking_flight"),
    path('see_booking', views.see_booking, name='see_booking'),
    path('cancel_booking', views.cancel_booking, name='cancel_booking'),
    path('change_seat', views.change_seat, name='change_seat'),
]