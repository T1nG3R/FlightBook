from datetime import datetime
from uuid import UUID

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import Profile, Ticket, BuyTicket
from .utils.sorting import *


# Create your views here.
def index(request):
    if str(request.user) != 'AnonymousUser' and not request.user.is_superuser:
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)

        tickets = list(Ticket.objects.all())
        tickets.reverse()
        return render(request, 'index.html', {'user_profile': user_profile, 'tickets': tickets[:10]})
    else:
        tickets = list(Ticket.objects.all())
        tickets.reverse()
        return render(request, 'index.html', {'tickets': tickets[:10], 'user': 'AnonymousUser'})


def signup(request):
    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        company = request.POST['company']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email,
                                                password=password, first_name=firstname, last_name=lastname)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, firstname_user=firstname,
                                                     lastname_user=lastname, mail_user=email, company=company)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Not correct Username or Password')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        user_profile.firstname_user = request.POST['first_name']
        user_profile.lastname_user = request.POST['last_name']
        user_profile.mail_user = request.POST['email']

        date_of_birth = request.POST['date_of_birth']
        if date_of_birth != '':
            user_profile.date_of_birth_user = date_of_birth

        if 'company' in request.POST:
            company = request.POST['company']
            tickets = Ticket.objects.filter(company=user_profile.company, username=request.user.username)
            user_profile.company = company
            for i in tickets:
                i.company = company
                i.save()

        user_profile.phone_user = request.POST['phone']

        if request.FILES.get('profile_picture') is not None:
            user_profile.profileimg = request.FILES.get('profile_picture')

        user_profile.save()
        return profile(request, request.user.username)
    return render(request, 'settings.html', {'user_profile': user_profile})


@login_required(login_url='signin')
def delete_profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    if request.user.username == pk:
        user_object.delete()
        user_profile.delete()
        return redirect('/')
    else:
        return render(request, 'permission-denied.html')


@login_required(login_url='signin')
def add_ticket(request):
    users = Profile.objects.all()
    company_profiles = [profile.user.username for profile in users if profile.company != '']
    if str(request.user.username) not in company_profiles:
        return render(request, 'permission-denied.html')
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        destination1 = request.POST['destination1']
        destination2 = request.POST['destination2']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        price = request.POST['price']
        amount = request.POST['amount']

        new_post = Ticket.objects.create(company=user_profile.company, destination1=destination1,
                                         destination2=destination2, date=departure_date, time=departure_time,
                                         username=user_object.username, price=price, amount=amount)
        new_post.save()
        return redirect('/')
    else:
        return render(request, 'add-ticket.html', {'user_profile': user_profile})


@login_required(login_url='signin')
def buy_ticket(request):
    user_profile = Profile.objects.get(user=request.user)
    ticket_id = request.GET.get('ticket_id')
    ticket = Ticket.objects.get(id=ticket_id)

    return render(request, "buy-ticket.html", {'user_profile': user_profile, 'ticket': ticket})


@login_required(login_url='signin')
def complete_purchase(request):
    user_profile = Profile.objects.get(user=request.user)
    ticket_id = request.POST.get('ticket_id')
    ticket = Ticket.objects.get(id=ticket_id)

    if ticket.amount <= 0:
        messages.info(request, 'No tickets left')
        return render(request, "buy-ticket.html", {'user_profile': user_profile, 'ticket': ticket})
    elif (datetime.today() - datetime.strptime(request.POST['date_of_birth'], "%Y-%m-%d")).days >= 18 * 365:
        username = request.user.username
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        date_of_birth = request.POST['date_of_birth']
        phone = request.POST['phone']

        ticket.amount -= 1
        ticket.save()

        new_bought = BuyTicket.objects.create(ticket_id=ticket_id, username=username, firstname=firstname,
                                              lastname=lastname, email=email, date_of_birth=date_of_birth, phone=phone)
        new_bought.save()

        return redirect('/')
    else:
        messages.info(request, 'Your age must be greater than 18')
        return render(request, "buy-ticket.html", {'user_profile': user_profile, 'ticket': ticket})


@login_required(login_url='signin')
def profile(request, pk):
    if request.user.username != pk:
        return render(request, 'permission-denied.html')

    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    if user_profile.company == '':
        tickets = BuyTicket.objects.filter(username=pk)
        user_tickets = [str(ticket).split() for ticket in tickets]
        tickets_data = [Ticket.objects.get(id=UUID(str(i[0]))) for i in user_tickets]
        for i in range(len(tickets_data)):
            user_tickets[i].insert(0, tickets_data[i])
    else:
        user_tickets = Ticket.objects.filter(username=pk)
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_tickets': user_tickets,
    }
    return render(request, "profile.html", context)


@login_required(login_url='signin')
def edit_ticket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    if ticket.username != request.user.username:
        return render(request, 'permission-denied.html')

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        print(request.POST)
        destination1 = request.POST['destination1']
        destination2 = request.POST['destination2']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        price = request.POST['price']
        amount = request.POST['amount']

        ticket.destination1 = destination1
        ticket.destination2 = destination2
        ticket.date = departure_date
        ticket.time = departure_time
        ticket.price = price
        ticket.amount = amount
        ticket.save()
        return redirect('/')
    else:
        return render(request, 'edit-ticket.html', {'user_profile': user_profile, 'ticket': ticket})


@login_required(login_url='signin')
def delete_ticket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    if request.user.username == ticket.username:
        user_object = User.objects.get(username=request.user.username)
        ticket.delete()
        return redirect('/profile/' + str(user_object.username))
    else:
        return render(request, 'permission-denied.html')


def search_tickets(request_get):
    destination1 = request_get.get('destination1', '')
    destination2 = request_get.get('destination2', '')
    departure_date = request_get.get('departure_date', '')
    company = request_get.get('company', '')
    if str(company) != '':
        return Ticket.objects.filter(company=company)
    elif str(departure_date) == '':
        return Ticket.objects.filter(destination1=destination1, destination2=destination2)
    else:
        return Ticket.objects.filter(destination1=destination1, destination2=destination2, date=departure_date)


def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    tickets = search_tickets(request.GET)
    date_value = str(request.GET.get('departure_date')) == ''

    if 'sort' in request.GET:
        if 'price' in request.GET.get('sort'):
            tickets = sort_by_price(tickets, request.GET.get('sort'))
        elif 'datetime' in request.GET.get('sort'):
            tickets = sort_by_datetime(tickets, request.GET.get('sort'))
        elif 'amount' in request.GET.get('sort'):
            tickets = sort_by_amount(tickets, request.GET.get('sort'))

    context = {
        'user_profile': user_profile,
        'tickets': tickets,
        'tickets_size': len(tickets),
        'date_value': date_value
    }
    return render(request, 'search.html', context)
