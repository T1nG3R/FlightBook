from uuid import UUID
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Ticket, BuyTicket
from datetime import date, datetime


# Create your views here.
def index(request):
    if str(request.user) != 'AnonymousUser':
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)

        tickets = list(Ticket.objects.all())
        tickets.reverse()
        return render(request, 'index.html', {'user_profile': user_profile, 'tickets': tickets[:10]})
    else:
        tickets = Ticket.objects.all()[:10]
        return render(request, 'index.html', {'tickets': tickets, 'user': str(request.user)})


def signup(request):
    if request.method == "POST":
        # print(request.POST)
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

                # log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create a Profile object for the new user
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
        # print(request.POST)
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
        # print(request.POST)
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        date_of_birth = request.POST['date_of_birth']
        phone = request.POST['phone']
        if 'company' in request.POST:
            company = request.POST['company']
            tickets = Ticket.objects.filter(company=user_profile.company, username=request.user.username)
            # print(tickets)
            user_profile.company = company
            for i in tickets:
                i.company = company
                # print(i.company)
                i.save()

        if request.FILES.get('profile_picture') is not None:
            user_profile.profileimg = request.FILES.get('profile_picture')
        user_profile.firstname_user = firstname
        user_profile.lastname_user = lastname
        user_profile.mail_user = email
        if date_of_birth != '':
            user_profile.date_of_birth_user = date_of_birth
        user_profile.phone_user = phone

        user_profile.save()
        return profile(request, request.user.username)
    return render(request, 'settings.html', {'user_profile': user_profile})


@login_required(login_url='signin')
def add_ticket(request):
    users = Profile.objects.all()
    company_profiles = [i.user.username for i in users if i.company != '']
    if str(request.user.username) not in company_profiles:
        return HttpResponse("<h1 style=\"color: red; text-align: center; margin: 20% auto; \" >Permission Denied</h1>")
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        destination1 = request.POST['destination1']
        destination2 = request.POST['destination2']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        price = request.POST['price']

        new_post = Ticket.objects.create(company=user_profile.company, destination1=destination1,
                                         destination2=destination2, date=departure_date, time=departure_time,
                                         username=user_object.username, price=price)
        new_post.save()
        return redirect('/')
    else:
        return render(request, 'add-ticket.html', {'user_profile': user_profile})


# @login_required(login_url='signin')
# def buy_ticket(request):
#     user_profile = Profile.objects.get(user=request.user)
#     username = request.user.username
#     ticket_id = request.GET.get('ticket_id')
#
#     ticket = Ticket.objects.get(id=ticket_id)
#     buy_filter = BuyTicket.objects.filter(ticket_id=ticket_id, username=username)
#     if len(buy_filter) == 0:
#         new_bought = BuyTicket.objects.create(ticket_id=ticket_id, username=username)
#         new_bought.save()
#         return redirect('/')
#     else:
#         buy_filter.delete()
#         return redirect('/')


@login_required(login_url='signin')
def buy_ticket(request):
    user_profile = Profile.objects.get(user=request.user)
    username = request.user.username
    ticket_id = request.GET.get('ticket_id')
    ticket = Ticket.objects.get(id=ticket_id)

    return render(request, "buy-ticket.html", {'user_profile': user_profile, 'ticket': ticket})


@login_required(login_url='signin')
def complete_purchase(request):
    user_profile = Profile.objects.get(user=request.user)
    ticket_id = request.POST.get('ticket_id')
    ticket = Ticket.objects.get(id=ticket_id)
    if (datetime.today() - datetime.strptime(request.POST['date_of_birth'], "%Y-%m-%d")).days >= 18 * 365:
        username = request.user.username
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        date_of_birth = request.POST['date_of_birth']
        phone = request.POST['phone']

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
        return HttpResponse("<h1 style=\"color: red; text-align: center; margin: 20% auto; \" >Permission Denied</h1>")
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    if user_profile.company == '':
        tickets = BuyTicket.objects.filter(username=pk)
        user_tickets = [str(t).split() for t in tickets]
        tickets_data = [Ticket.objects.get(id=UUID(str(i[0]))) for i in user_tickets]
        for i in range(len(tickets_data)):
            user_tickets[i].insert(0, tickets_data[i])
    else:
        user_tickets = Ticket.objects.filter(username=pk)
    # print(user_tickets)
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
        return HttpResponse("<h1 style=\"color: red; text-align: center; margin: 20% auto; \" >Permission Denied</h1>")
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        print(request.POST)
        destination1 = request.POST['destination1']
        destination2 = request.POST['destination2']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        price = request.POST['price']

        ticket.destination1 = destination1
        ticket.destination2 = destination2
        ticket.date = departure_date
        ticket.time = departure_time
        ticket.price = price
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
        return HttpResponse("<h1 style=\"color: red; text-align: center; margin: 20% auto; \" >Permission Denied</h1>")


def search_tickets(destination1, destination2, departure_date):
    if str(departure_date) == '':
        return Ticket.objects.filter(destination1=destination1, destination2=destination2)
    else:
        return Ticket.objects.filter(destination1=destination1, destination2=destination2, date=departure_date)


def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    destination1 = request.GET.get('destination1', '')
    destination2 = request.GET.get('destination2', '')
    departure_date = request.GET.get('departure_date', '')
    tickets = search_tickets(destination1, destination2, departure_date)

    context = {
        'user_profile': user_profile,
        'tickets': tickets,
        'tickets_size': len(tickets)
    }
    return render(request, 'search.html', context)
