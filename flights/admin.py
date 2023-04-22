from django.contrib import admin
from .models import Aircrafts, Airlines, Flights, Seats, Bookings
# Register your models here.

# class AirlinesAdmin(admin.ModelAdmin):
#     list_display = ("al_id","starting_loc","destination")
# class AircraftsAdmin(admin.ModelAdmin):
#     # filter_horizontal = ("flights",)
#     list_display = ("ac_id","type","al_id","seats_capacity")

admin.site.register(Airlines)
admin.site.register(Aircrafts)
admin.site.register(Flights)
admin.site.register(Seats)
admin.site.register(Bookings)
# admin.site.register(Airlines, AirlinesAdmin)
# admin.site.register(Aircrafts, AircraftsAdmin)