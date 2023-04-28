from django.contrib import admin
from .models import Aircrafts, Airlines, Flights, Seats, Bookings
# Register your models here.


admin.site.register(Airlines)
admin.site.register(Aircrafts)
admin.site.register(Flights)
admin.site.register(Seats)
admin.site.register(Bookings)