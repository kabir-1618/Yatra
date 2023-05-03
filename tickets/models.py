from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)
    regno = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    email = models.CharField(max_length=255, unique=True)
    phoneno = models.CharField(max_length=100)
    dept = models.CharField(max_length=100)
    collegename = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=1000)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
      return self.name


class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    category_id = models.IntegerField()
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default="")
    short_description = models.CharField(max_length=500, default="")
    image_url = models.CharField(max_length=1000, default="")
    name_of_incharge1 = models.CharField(max_length=100, default="")
    phone_of_incharge1 = models.CharField(max_length=100, default="")
    name_of_incharge2 = models.CharField(max_length=100, default="")
    phone_of_incharge2 = models.CharField(max_length=100, default="")
    name_of_incharge3 = models.CharField(max_length=100, default="")
    phone_of_incharge3 = models.CharField(max_length=100, default="")
    contact_mail= models.CharField(max_length=100, default="")
    prize = models.CharField(default="", max_length=100)
    time_of_event = models.CharField(max_length=50, default="")
    duration_in_hours = models.CharField(max_length=5, default="")
    venue = models.CharField(max_length=50, default="")
    name_of_hosting_club = models.CharField(max_length=100, default="")
    rules = models.CharField(max_length=5000)
    selection = models.CharField(max_length=50, default="")
    team_event = models.BooleanField(default=False)
    team_min = models.IntegerField(default=0)
    team_max = models.IntegerField(default=0)
    pay = models.IntegerField(default=0)
    max_reg = models.IntegerField(default=10**9)
    upload = models.BooleanField(default=False)
    day = models.IntegerField(default=1)
    registrations = models.IntegerField(default=0)

    def __str__(self):
      return self.name

class MainEvent(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, unique=True)
    day1 = models.BooleanField(default=False)
    day2 = models.BooleanField(default=False)
    day3 = models.BooleanField(default=False)
    combo =models.BooleanField(default=False)
    day1Scan = models.IntegerField(default=0)
    day2Scan = models.IntegerField(default=0)
    day3Scan = models.IntegerField(default=0)
    day1Image = models.CharField(max_length=1000, default="")
    day2Image=models.CharField(max_length=1000, default="")
    day3Image=models.CharField(max_length=1000, default="")
    premium1 = models.BooleanField(default=False)
    premium2 = models.BooleanField(default=False)
    premium3 = models.BooleanField(default=False)

    def __str__(self):
      return str(self.id) + ") "+ self.email

class EventRegister(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    event_id = models.IntegerField()
    team_name = models.CharField(max_length=50, default="")
    team_mates =  models.CharField(max_length=5000, default="")
    upload_link = models.CharField(max_length=1000, default="")
    pay_there = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    def __str__(self):
      return str(self.id) + ") "+ self.email
    

class TeamMates(models.Model):
   id = models.AutoField(primary_key=True)
   team_mate = models.CharField(max_length=255)
   event_register_id = models.IntegerField()
   event_id = models.IntegerField()
   verified = models.BooleanField(default=False)

   def __str__(self):
      return str(self.id) + ") "+ self.team_mate
   

class ForgotPassword(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=100, default="")

    def __str__(self):
      return str(self.id) + ") "+ self.email
    
class PremimumTicket(models.Model):
  id = models.AutoField(primary_key=True)
  email = models.CharField(max_length=255)
  day = models.IntegerField()

  def __str__(self):
    return str(self.id) + ") "+ self.email
  
class Category(models.Model):
   category_id = models.IntegerField()
   category_name = models.CharField(max_length=100)
   image_url = models.CharField(max_length=1000, default="")

   def __str__(self):
      return self.category_name
   
class Transaction(models.Model):
   payment_id = models.CharField(max_length=100)
   payment_status = models.CharField(max_length=100)
   payment_request_id = models.CharField(max_length=100)
   amount = models.IntegerField()
   email = models.CharField(max_length=255)
   status = models.CharField(max_length=100)
   purpose = models.CharField(max_length=100)

   def __str__(self):
      return self.email

class Merch(models.Model):
  id = models.AutoField(primary_key=True)
  email = models.CharField(max_length=255)
  size = models.CharField(max_length=100)

  def __str__(self):
    return str(self.id) + ") "+ self.email