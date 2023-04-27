from django.db import models
from users.models import User

# Create your models here.



class Airlines(models.Model):
    al_id = models.AutoField(primary_key=True, blank=True, null=False)
    starting_loc = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    name = models.CharField(max_length=100, default='')


class Aircrafts(models.Model):
    ac_id = models.AutoField(primary_key=True, blank=True, null=False)
    type = models.CharField(max_length=50)
    al = models.ForeignKey(Airlines, on_delete=models.CASCADE)
    seats_capacity = models.IntegerField(blank=True, null=False)

class FlightStatusEnum(models.IntegerChoices):
    OPEN = 0,'Open'
    CLOSED = 1, 'Closed'

class Flights(models.Model):
    f_id = models.AutoField(primary_key=True, blank=True, null=False)
    departure_time = models.DateTimeField(blank=True, null=True)
    arrive_time = models.DateTimeField(blank=True, null=True)
    al = models.ForeignKey(Airlines, on_delete=models.CASCADE)
    status = models.IntegerField(choices=FlightStatusEnum.choices) #0-Open, 1-Closed
    seats_left = models.IntegerField(blank=True, null=False)
    ac = models.ForeignKey(Aircrafts, on_delete=models.CASCADE)

class SeatClassEnum(models.IntegerChoices):
    FIRST = 0,'First'
    BUSINESS = 1,'Business'
    ECONOMICS = 2,'Economics'

class SeatStatusEnum(models.IntegerChoices):
    BOOKED = 0, 'Booked'
    AVAILABLE = 1, 'Available'
    SAVED = 2, 'Saved'

class Seats(models.Model):
    s_id = models.AutoField(primary_key=True, blank=True, null=False)
    f = models.ForeignKey(Flights, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    cls = models.IntegerField(choices=SeatClassEnum.choices) #seat class  0-First, 1-Business, 2-Economics.
    price = models.IntegerField()
    status = models.IntegerField(choices=SeatStatusEnum.choices) #0-Booked, 1-Available, 2-Saved

class BookStatusEnum(models.IntegerChoices):
    PENDING = 0, 'Pending'
    FINISHED = 1, 'Finished'
    REFUNDING = 2, 'Refunding'

class BookPaymentEnum(models.IntegerChoices):
    VISA = 0, 'Visa'
    PAYPAL = 1, 'PayPal'
    STRIPE = 2, 'Stripe'
    APPLEPAY = 3, 'Apple Pay'

class Bookings(models.Model):
    b_id = models.AutoField(primary_key=True, blank=True, null=False)
    f = models.ForeignKey(Flights, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    s = models.ForeignKey(Seats, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)
    payment_method = models.IntegerField(choices=BookPaymentEnum.choices) #0-4 for different payment platforms. 0 PayPal,1 Due ,2 Stripe,3 Payline
    status = models.IntegerField(choices=BookStatusEnum.choices) #0-Pending, 1-Finished, 2-Refunding


