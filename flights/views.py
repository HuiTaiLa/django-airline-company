from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import time
from django.db.models import Min
from datetime import datetime

from users.models import User
from .models import Airlines, Aircrafts, Seats, Flights, Bookings
from django.core.paginator import Paginator
# Create your views here.
def index(request):
    if str(request.user) is 'AnonymousUser':
        return render(request, "login.html", {
            "message": "please login"
        })
    page = request.GET.get('page', 1)  # page num
    limit = request.GET.get('limit', 2)  # page capacity

    res = []
    flights = Flights.objects.all()
    index = 1
    for _ in flights:
        item = {}
        lowest_price = Seats.objects.filter(f=_.f_id).all().aggregate(price=Min('price'))['price']
        item['lowest_price'] = lowest_price
        item['flight_id'] = _.f_id
        item['index'] = index
        item['travel_time'] = _.departure_time.strftime("%H:%M")
        item['air_line_name'] = _.al.name
        index += 1
        res.append(item)
    paginator = Paginator(res, limit)
    page_1 = paginator.get_page(page)
    return render(request, "flights.html",{
        "code": '200',
        "data": page_1.object_list,
        'page_1':page_1
    })

def flight(request, flight_id):
    if str(request.user) is 'AnonymousUser':
        return render(request, "login.html", {
            "message": "please login"
        })
    flight = Flights.objects.get(pk=flight_id)
    data = {}
    data['id'] = flight.f_id
    data['departure_time'] = flight.departure_time.strftime('%Y-%m-%d %H:%M')
    data['arrival_time'] = flight.arrive_time.strftime('%Y-%m-%d %H:%M')
    data['departure_loc'] = flight.al.starting_loc
    data['seats_left'] = flight.seats_left
    seats = Seats.objects.filter(f=flight.f_id, status=1).all()
    for seat in seats:
        seat.status = 'Booked' if seat.status == 0 else seat.status
        seat.status = 'Available' if seat.status == 1 else seat.status
        seat.status = 'Saved' if seat.status == 2 else seat.status
    data['seats'] = seats
    s = flight.status
    s = 'Open' if s == 0 else 'Closed'
    data['status'] = s
    data['aircraft_id'] = flight.ac

    return render(request, "flight.html", {
        "flight" : data
    })

def get_flight_details(request):
    if str(request.user) is 'AnonymousUser':
        return render(request, "login.html", {
            "message": "please login"
        })
    fid = request.GET['flight_id']
    if fid is None or fid.strip() == '':
        return []
    flight = Flights.objects.get(pk=fid)
    data = {}
    data['departure_time'] = flight.departure_time.strftime('%Y-%m-%d %H:%M')
    data['arrival_time'] = flight.arrive_time.strftime('%Y-%m-%d %H:%M')
    data['departure_loc'] = flight.al.starting_loc
    data['seats_left'] = flight.seats_left
    seats = Seats.objects.filter(f=flight.f_id).all()
    data['seats'] = seats
    s = flight.status
    s = 'Open' if s == 0 else 'Closed'
    data['status'] = s
    data['aircraft_id'] = flight.ac
    return data

def list_flights(request):
    if str(request.user) is 'AnonymousUser':
        return render(request, "login.html", {
            "message": "please login"
        })
    if request.method == "POST":
        departure_loc = request.POST["departure_loc"]
        arrival_loc = request.POST["arrival_loc"]
        travel_date = request.POST["travel_date"]
        num_people = request.POST["num_people"]
        seat_class = request.POST["seat_class"]
        # tranformation
        seat_class = 0 if seat_class == 'First' else seat_class
        seat_class = 1 if seat_class == 'Business' else seat_class
        seat_class = 2 if seat_class == 'Economics' else seat_class

        res = []
        flights = Flights.objects.all()
        index = 1
        for _ in flights:
            item = {}
            print(travel_date)
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
            res.append(item)
        return render(request, "flights.html",{
                "data": res
            })



def book(request):
    if str(request.user) is 'AnonymousUser':
        return render(request, "login.html", {
            "message": "please login"
        })
    if request.method == "POST":
        fid = request.POST['flight_id']
        user_ids = request.POST['user_id']
        number_people = request.POST['number_people']
        seat_ids = request.POST['seat_id']
        payment_method = request.POST['payment_method']
        if fid is None or fid.strip() == '' or user_ids is None or user_ids.strip() == '' or number_people is None or int(number_people) <= 0\
                or seat_ids is None or seat_ids.strip() == '' or payment_method is None or payment_method.strip() == '':
            return HttpResponseRedirect(reverse("flights"))
        seat_ids = seat_ids.split()
        user_ids = user_ids.split()
        number_people = int(number_people)
        if len(seat_ids) != len(user_ids) or len(seat_ids) != number_people:
            return HttpResponseRedirect(reverse("flights"))

        payment_method = 0 if payment_method=='PayPal' else payment_method
        payment_method = 1 if payment_method == 'Due' else payment_method
        payment_method = 2 if payment_method == 'Stripe' else payment_method
        payment_method = 3 if payment_method == 'Payline' else payment_method
        flight = Flights.objects.get(pk=fid)
        if flight.status == 1 or flight.seats_left <= 0:
            return HttpResponseRedirect(reverse("flights"))

        total_cost = 0
        for s_id in seat_ids:
            s = Seats.objects.get(pk=s_id)
            if s.status != 1:
                return HttpResponseRedirect(reverse("flights"))
            total_cost += s.price

        u = User.objects.get(pk=request.user.user_id)
        if total_cost > u.balance:
            print('balance is not enough!')
            return HttpResponseRedirect(reverse("flights"))
        res = []
        #update users balance
        u.balance -= total_cost
        u.save()

        for i in range(number_people):
            flight=Flights.objects.get(pk=fid)
            us = User.objects.get(pk=user_ids[i])
            seat = Seats.objects.get(pk=seat_ids[i])
            book = Bookings(f=flight,user=u,s=seat,first_name=us.first_name,last_name=us.last_name,date=datetime.now(),payment_method=payment_method,status=1)
            book.save()

            seat.status = 0
            seat.save()
            res.append(book.b_id)

        #update left seat
        flight.seats_left -= number_people
        flight.save()

        # return render(request, "see_booking.html",{
        # })
        return HttpResponseRedirect(reverse("see_booking"))


def see_booking(request, *args):
    if str(request.user) is 'AnonymousUser':
        return render(request, "login.html", {
            "message": "please login"
        })
    # print(*args)
    msg = request.GET.get('message','')
    data = Bookings.objects.filter(user=request.user.user_id)
    for t in data:
        t.status = 'Pending' if t.status == 0 else t.status
        t.status = 'Finished' if t.status == 1 else t.status
        t.status = 'Refunding' if t.status == 2 else t.status
    return render(request, "see_booking.html",{
            "book_list": data,
        'message': msg
        })

def cancel_booking(request):
    if str(request.user) is 'AnonymousUser':
        return render(request, "login.html", {
            "message": "please login"
        })
    if request.method == "POST":
        fid = request.POST['flight_id']
        booking_id = request.POST['booking_id']

        if fid is None or fid.strip() == '' or booking_id is None or booking_id.strip() == '':
            return HttpResponseRedirect(reverse("see_booking"))

        flight = Flights.objects.get(pk=fid)
        if flight.status == 1:
            return HttpResponseRedirect(reverse("see_booking"))

        book = Bookings.objects.get(pk=booking_id)
        if book.status != 1:
            return HttpResponseRedirect(reverse("see_booking"))

        seat = book.s
        seat.status = 1 # Avalable
        seat.save()

        book.status = 2
        book.save()

        # refund to user balance
        u = User.objects.get(pk=request.user.user_id)

        u.balance += book.s.price
        u.save()

        flight.seats_left += 1
        flight.save()
        return HttpResponseRedirect(reverse("see_booking"))


def change_seat(request):
    if str(request.user) is 'AnonymousUser':
        return render(request, "login.html", {
            "message": "please login"
        })
    if request.method == "POST":
        fid = request.POST['flight_id']
        booking_id = request.POST['booking_id']
        new_seat_id = request.POST['new_seat_id']

        if fid is None or fid.strip() == '' or booking_id is None or booking_id.strip() == '' or new_seat_id is None or new_seat_id.strip() == '':
            return HttpResponseRedirect(reverse("see_booking"))

        flight = Flights.objects.get(pk=fid)
        if flight.status == 1:
            return HttpResponseRedirect(reverse("see_booking"))

        book = Bookings.objects.get(pk=booking_id)
        if book.status != 1:
            return HttpResponseRedirect(reverse("see_booking"))

        new_seat = Seats.objects.get(pk=new_seat_id)
        if new_seat.status != 1 and new_seat.price != book.s.price:
            return HttpResponseRedirect(reverse("see_booking"))

        if new_seat.f.f_id != int(fid):
            return HttpResponseRedirect(reverse("see_booking"))

        # update new_seat status and old seat status
        print(3)
        new_seat.status = 0
        new_seat.save()
        print('new seat %s status changed!'%new_seat.s_id)
        s = book.s
        s.status = 1
        s.save()
        print('old seat %s status changed!'%s.s_id)
        book.s = new_seat
        book.save()
        return HttpResponseRedirect("/flights/see_booking?message=%s"%'changed seat success')
