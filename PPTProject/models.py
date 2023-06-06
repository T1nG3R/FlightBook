from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()


# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    profileimg = models.ImageField(upload_to='profile_imges', default='blank-profile-picture.png')
    firstname_user = models.CharField(blank=True, max_length=100)
    lastname_user = models.CharField(blank=True, max_length=100)
    company = models.CharField(blank=True, max_length=100)
    date_of_birth_user = models.DateField(null=True, blank=True)
    mail_user = models.EmailField(blank=True, max_length=50)
    phone_user = models.CharField(blank=True, max_length=12)

    def __str__(self):
        return self.user.username


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(blank=True, max_length=100)
    company = models.CharField(max_length=100)
    destination1 = models.CharField(blank=True, max_length=100)
    destination2 = models.CharField(blank=True, max_length=100)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    price = models.IntegerField(null=True)
    amount = models.IntegerField(null=True)

    def __str__(self):
        return self.destination1 + " " + self.destination2 + " " + str(self.date) + " " + str(self.time) + str(
            self.amount)


class BuyTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    ticket_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)
    firstname = models.CharField(blank=True, max_length=100)
    lastname = models.CharField(blank=True, max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True, max_length=50)
    phone = models.CharField(blank=True, max_length=12)

    def __str__(self):
        return self.ticket_id + " " + self.firstname + " " + self.lastname + " " + str(
            self.date_of_birth) + " " + self.email + " " + self.phone + " " + str(self.id)
