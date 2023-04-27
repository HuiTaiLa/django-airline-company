import json

from django.http import HttpResponseRedirect
from django.urls import reverse
import time
from django.db.models import Min
from datetime import datetime

from users.models import User
from .models import Airlines, Aircrafts, Seats, Flights, Bookings, FlightStatusEnum, SeatClassEnum, SeatStatusEnum, BookStatusEnum, BookPaymentEnum

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def get_flight_details(request):
    fid = request.GET.get('flight_id',default='')
    res = {}
    if fid is None or str(fid).strip() == '':
        res['code'] = 200
        res['msg'] = 'The request parameter flight_id is required!'
        # res['data'] = None
        return JsonResponse(res)
    flight = Flights.objects.get(pk=fid)
    data = {}
    data['departure_time'] = flight.departure_time.strftime('%Y-%m-%d %H:%M')
    data['arrival_time'] = flight.arrive_time.strftime('%Y-%m-%d %H:%M')
    data['departure_loc'] = flight.al.starting_loc
    data['seats_left'] = flight.seats_left
    seats = Seats.objects.filter(f=flight.f_id).all()
    l = []
    for s in seats:
        dk = {}
        dk['seat_id'] = s.s_id
        dk['seat_number'] = s.seat_number
        dk['class'] = SeatClassEnum(s.cls).label
        dk['price'] = s.price
        dk['status'] = SeatStatusEnum(s.status).label
        l.append(dk)
    data['seats'] = l
    data['status'] = FlightStatusEnum(flight.status).label
    data['aircraft_id'] = flight.ac.ac_id
    # res['data'] = data
    # res['code'] = 200
    # res['msg'] = 'Request success!'
    data['code'] = 200
    return JsonResponse(data)

def get_flights(request):
    departure_loc = request.GET.get("departure_loc",'')
    arrival_loc = request.GET.get("arrival_loc",'')
    travel_date = request.GET.get("travel_date",'')
    num_people = request.GET.get("num_people",'')
    seat_class = request.GET.get("seat_class",'')

    res = {}
    data = []
    flights = Flights.objects.all()
    index = 1
    for _ in flights:
        item = {}
        if travel_date is not None and str(travel_date).strip() != '' and _.departure_time.strftime('%Y-%m-%d') != travel_date:
            continue
        if departure_loc is not None and str(departure_loc).strip() != '':
            sl = _.al.starting_loc
            if sl.casefold() != departure_loc.casefold():
                continue
        if arrival_loc is not None and str(arrival_loc).strip() != '':
            dest = _.al.destination
            if dest.casefold() != arrival_loc.casefold():
                continue

        if num_people is not None and str(num_people).strip() != '' and _.seats_left < int(num_people):
            continue

        if seat_class is not None and str(seat_class).strip() != '':
            c = Seats.objects.filter(f=_.f_id, cls=seat_class).count()
            if c == 0:
                continue

        lowest_price = Seats.objects.filter(f=_.f_id).all().aggregate(price=Min('price'))['price']
        item['lowest_price'] = lowest_price
        item['flight_id'] = _.f_id
        item['index'] = index
        item['travel_time'] = _.departure_time.strftime("%H-%M")
        item['air_line_name'] = _.al.name
        index += 1
        data.append(item)
    res['list'] = data
    res['code'] = 200
    # res['msg'] = 'Request success!'
    return JsonResponse(res)

@csrf_exempt
def booking_flight(request):
    if request.method == "POST":
        req = json.loads(request.body)
        res = {}
        fid = req['flight_id']
        user_id = req['user_id']
        number_people = req['number_people']
        seats = req['seats']
        payment_method = req['payment_method']
        if fid is None or int(fid)<0 or user_id is None or int(user_id)<0 or number_people is None or int(number_people) <= 0\
                or seats is None or type(seats) != list or payment_method is None or int(payment_method)<0 or int(payment_method)>=4:
            res['code'] = 200
            res['msg'] = 'your post body is wrong！'
            res['booking_ids'] = None
            return JsonResponse(res)
        number_people = int(number_people)
        if len(seats) != number_people:
            res['code'] = 200
            res['msg'] = 'The number of seats you booked does not match the number of people！'
            res['booking_ids'] = None
            return JsonResponse(res)
        fid = int(fid)
        user_id = int(user_id)
        payment_method = int(payment_method)
        flight = Flights.objects.get(pk=fid)
        if flight.status == FlightStatusEnum.CLOSED or flight.seats_left <= 0:
            res['code'] = 200
            res['msg'] = 'The booking flight not meet requirement！'
            res['booking_ids'] = None
            return JsonResponse(res)

        total_cost = 0
        for seat in seats:
            s = Seats.objects.get(pk=seat['seat_id'])
            if s.status != SeatStatusEnum.AVAILABLE:
                res['code'] = 200
                res['msg'] = 'The booking seats not meet requirement！'
                res['booking_ids'] = None
                return JsonResponse(res)
            total_cost += s.price

        u = User.objects.get(pk=user_id)
        if total_cost > u.balance:
            res['code'] = 200
            res['msg'] = 'balance is not enough!'
            res['booking_ids'] = None
            return JsonResponse(res)
        bookids = []
        #update users balance
        u.balance -= total_cost
        u.save()

        for i in range(number_people):
            flight=Flights.objects.get(pk=fid)
            # us = User.objects.get(pk=user_id[i])
            seat = Seats.objects.get(pk=seats[i]['seat_id'])
            book = Bookings(f=flight,user=u,s=seat,date=datetime.now(),payment_method=payment_method,status=BookStatusEnum.FINISHED)
            book.save()

            seat.status = SeatStatusEnum.BOOKED
            seat.save()
            bookids.append(book.b_id)

        #update left seat
        flight.seats_left -= number_people
        flight.save()
        res['code'] = 200
        res['msg'] = 'book success!'
        res['booking_ids'] = bookids
        return JsonResponse(res)

@csrf_exempt
def cancel_booking(request):
    if request.method == "POST":
        req = json.loads(request.body)
        res = {}
        fid = req['flight_id']
        user_id = req['user_id']
        booking_id = req['booking_id']

        if fid is None or int(fid) <0 or booking_id is None or int(booking_id)<0 or user_id is None or int(user_id)<0 :
            res['code'] = 200
            res['msg'] = 'your post body is wrong！'
            return JsonResponse(res)

        fid = int(fid)
        user_id = int(user_id)
        booking_id = int(booking_id)

        flight = Flights.objects.get(pk=fid)
        if flight.status == FlightStatusEnum.CLOSED:
            res['code'] = 200
            res['msg'] = 'The flight not meet requirement！'
            return JsonResponse(res)

        book = Bookings.objects.get(pk=booking_id,f=fid,user=user_id)
        if book.status != BookStatusEnum.FINISHED:
            res['code'] = 200
            res['msg'] = 'The book status not meet requirement！'
            return JsonResponse(res)

        seat = book.s
        seat.status = SeatStatusEnum.AVAILABLE # Avalable
        seat.save()

        book.status = BookStatusEnum.REFUNDING
        book.save()

        # refund to user balance
        u = User.objects.get(pk=user_id)

        u.balance += book.s.price
        u.save()

        flight.seats_left += 1
        flight.save()
        res['code'] = 200
        res['msg'] = 'The book cancels success！'
        return JsonResponse(res)

@csrf_exempt
def alter_seat(request):
    if request.method == "POST":
        req = json.loads(request.body)
        res = {}
        fid = req['flight_id']
        user_id = req['user_id']
        booking_id = req['booking_id']
        new_seat_id = req['new_seat_id']

        if fid is None or int(fid)<0 or booking_id is None or int(booking_id)<0 or new_seat_id is None or int(new_seat_id)<0 or user_id is None or int(user_id)<0:
            res['code'] = 200
            res['msg'] = 'your post body is wrong！'
            return JsonResponse(res)

        fid = int(fid)
        user_id = int(user_id)
        booking_id = int(booking_id)
        new_seat_id = int(new_seat_id)

        flight = Flights.objects.get(pk=fid)
        if flight.status == FlightStatusEnum.CLOSED:
            res['code'] = 200
            res['msg'] = 'The flight not meet requirement！'
            return JsonResponse(res)

        book = Bookings.objects.get(pk=booking_id, user=user_id)
        if book.status != BookStatusEnum.FINISHED:
            res['code'] = 200
            res['msg'] = 'The book status not meet requirement！'
            return JsonResponse(res)

        if book.f.status == FlightStatusEnum.CLOSED:
            res['code'] = 200
            res['msg'] = 'The booked flight not meet requirement！'
            return JsonResponse(res)

        new_seat = Seats.objects.get(pk=new_seat_id)
        u = User.objects.get(pk=user_id)
        if new_seat.status != SeatStatusEnum.AVAILABLE:
            res['code'] = 200
            res['msg'] = 'The new seat status not meet requirement！'
            return JsonResponse(res)

        if new_seat.f.f_id != int(fid):
            res['code'] = 200
            res['msg'] = 'The new seat not match the flight!'
            return JsonResponse(res)

        if new_seat.price != book.s.price:
            res['code'] = 200
            res['msg'] = 'The new seat price not equals the old！'
            return JsonResponse(res)

        # update old book
        book.status = BookStatusEnum.REFUNDING
        book.save()
        # insert new book
        new_book = Bookings(f=flight, user=u, s=new_seat, date=datetime.now(), payment_method=book.payment_method,
                        status=BookStatusEnum.FINISHED)
        new_book.save()
        # update the old flight
        old_flight = book.f
        old_flight.seats_left += 1
        old_flight.save()
        # update new flight
        flight.seats_left -= 1
        flight.save()
        # update new_seat status and old seat status
        new_seat.status = SeatStatusEnum.BOOKED
        new_seat.save()
        print('new seat %s status changed!'%new_seat.s_id)
        s = book.s
        s.status = SeatStatusEnum.AVAILABLE
        s.save()
        print('old seat %s status changed!'%s.s_id)

        res['code'] = 200
        res['msg'] = 'alter seat success！'
        res['booking_id'] = new_book.b_id
        return JsonResponse(res)
