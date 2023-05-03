from rest_framework.decorators import api_view
from  rest_framework.response import Response
from datetime import date
import pandas as pd
from django.shortcuts import render, redirect, HttpResponse
import csv


from tickets.models import Event, MainEvent, User, Category, Transaction, EventRegister
# Create your views here.
@api_view(['GET'])
def eventinfo(request):
   try:
      x=request.query_params
      id=x["id"]
      if int(id)==0:
         return Response(Event.objects.filter().values())
      return Response(Event.objects.filter(category_id=id).values())
   except Exception as e:
      return Response({"message":"Failure"})

@api_view(['GET'])
def categoryinfo(request):
   return Response(Category.objects.values())

@api_view(['GET'])
def qrcodescanin(request):
   try:
      today = date.today()
      data=request.query_params
      s="static/tickets/"+data["data"]+".png"
      if today.month==3 and today.day==23 and today.year==2023:
         if MainEvent.objects.filter(day1Image=s):
            m=MainEvent.objects.get(day1Image=s)
            email=m.email
            u = User.objects.filter(email=email).values()
            d=[{}]
            d[0]["message"]="Valid"
            d[0]["day"]=1
            for i in u[0]:
               d[0][i]=u[0][i]
            if m.premium1:
               d[0]['premium']="Yes"
            else:
               d[0]['premium']='No'
            if m.day1Scan==1:
               d[0]["message"]="Duplicate"
               return Response(d)
            # m.day1Scan=1
            print(d)
            
            return Response(d)
         # return Response([{"message":"Invalid"}])
      if today.month==3 and today.day==24 and today.year==2023:
         
         if MainEvent.objects.filter(day2Image=s):
            m=MainEvent.objects.get(day2Image=s)
            email=m.email
            u = User.objects.filter(email=email).values()
            d=[{}]
            d[0]["message"]="Valid"
            d[0]["day"]=2
            for i in u[0]:
               d[0][i]=u[0][i]
            if m.premium2:
               d[0]['premium']="Yes"
            else:
               d[0]['premium']='No'
            if m.day2Scan==1:
               d[0]["message"]="Duplicate"
               return Response(d)
            return Response(d)
         # return Response([{"message":"Invalid"}])
      if today.month==3 and (today.day==25 or today.day==24) and today.year==2023:
         
         if MainEvent.objects.filter(day3Image=s):
            m=MainEvent.objects.get(day3Image=s)
            email=m.email
            u = User.objects.filter(email=email).values()
            d=[{}]
            d[0]["message"]="Valid"
            d[0]["day"]=3
            for i in u[0]:
               d[0][i]=u[0][i]
            if m.premium3:
               d[0]['premium']="Yes"
            else:
               d[0]['premium']='No'
            if m.day3Scan==1:
               d[0]["message"]="Duplicate"
               return Response(d)
            return Response(d)

         return Response([{"message":"Invalid"}])


      return Response([{"message":"Abe saale aaj toh culturals ka din hi nahi hain aaj kyu scan kar raha hain tu"}])
   except Exception as e:
      print(e)
      return Response([{"message":"Ask the data administrator to verify. There is some problem I guess"}])
   
@api_view(['GET'])
def qrcodescanout(request):
   try:
      today = date.today()
      data=request.query_params
      s="static/tickets/"+data["data"]+".png"
      if today.month==2 and today.day==27 and today.year==2023:
         if MainEvent.objects.filter(day1Image=s):
            m=MainEvent.objects.get(day1Image=s)
            if m.day1Scan==0:
               return Response({"message":"He didn't enter"})
            m.day1Scan=0
            email=m.email
            m.save()
            u = User.objects.filter(email=email).values()
            return Response(u)
         return Response({"message":"No such token"})
      if today.month==3 and today.day==24 and today.year==2023:
         
         if MainEvent.objects.filter(day2Image=s):
            m=MainEvent.objects.get(day2Image=s)
            if m.day2Scan==0:
               return Response({"message":"He didn't enter"})
            m.day2Scan=0
            email=m.email
            m.save()
            u = User.objects.filter(email=email).values()
            return Response(u)
         return Response({"message":"No such token"})
      if today.month==3 and today.day==25 and today.year==2023:
         
         if MainEvent.objects.filter(day3Image=s):
            m=MainEvent.objects.get(day3Image=s)
            if m.day3Scan==0:
               return Response({"message":"He didn't enter"})
            m.day3Scan=0
            email=m.email
            m.save()
            u = User.objects.filter(email=email).values()
            return Response(u)
         return Response({"message":"No such token"})


      return Response({"message":"Abe saale aaj toh din hi nahi hain aaj kyu re tu scan kar raha hain tu"})
   except Exception as e:
      print(e)
      return Response({"message":"Ask the data administrator to verify. There is some problem I guess"})
   

# def registrations_count(request):
#    try:
#       print("Entered")
#       d={}
#       d["day1_standardcount"]=len(MainEvent.objects.filter(day1=True, premium1=False).values())
#       d["day2_standardcount"]=len(MainEvent.objects.filter(day2=True, premium2=False).values())
#       d["day3_standardcount"]=len(MainEvent.objects.filter(day3=True, premium3=False).values())
#       d["day1_premiumcount"]=len(MainEvent.objects.filter( premium1=True).values())
#       d["day2_premiumcount"]=len(MainEvent.objects.filter( premium2=True).values())
#       d["day3_premiumcount"]=len(MainEvent.objects.filter( premium3=True).values())
#       print(d)
#       return Response({"messgae":"success"})
#    except Exception as e:
#       print(e)
#       return Response({"Message":"Failure"})

@api_view(['GET'])
def registrations_count(request):
   try:
      d={}
      d["day1_standardcount"]=len(MainEvent.objects.filter(day1=True, premium1=False).values())
      d["day2_standardcount"]=len(MainEvent.objects.filter(day2=True, premium2=False).values())
      d["day3_standardcount"]=len(MainEvent.objects.filter(day3=True, premium3=False).values())
      d["day1_premiumcount"]=len(MainEvent.objects.filter( premium1=True).values())
      d["day2_premiumcount"]=len(MainEvent.objects.filter( premium2=True).values())
      d["day3_premiumcount"]=len(MainEvent.objects.filter( premium3=True).values())
      # print(d)
      return Response(d)
   except Exception as e:
      print(e)
      return Response({"Message":"Failure"})
   
@api_view(['GET'])
def add_category(request):
   try:
      # return Response({"message":"Already Inserted"})
      lst={"Entertainment":1,
   "Literature":2,
   "GAMES":3,
   "PHOTGRAPHY":4,
   "ART":5,
   "TECHNICAL":6,
   "WORKSHOP/HANDS ON SESSION/CERTIFICATION":7,
   "DANCE":8,
   "MUSIC":9,
   "TALENT EXPRESSION":10,
   }
      j=1
      for i in lst:
         Category.objects.create(category_id=j, category_name=i)
         j+=1
      return Response({"message":"Success"})
   except:
      return Response({"message":"Failure"})
   

@api_view(['GET'])
def add_event(request):
   try:
      # return Response({"message":"Already Inserted"})
      lst={"Entertainment":1,
   "Literature":2,
   "GAMES":3,
   "PHOTGRAPHY":4,
   "ART":5,
   "TECHNICAL":6,
   "WORKSHOP/HANDS ON SESSION/CERTIFICATION":7,
   "DANCE":8,
   "MUSIC":9,
   "TALENT EXPRESSION":10,
   }
      df=pd.read_excel("events.xlsx")
      columns=list(df.columns)[1:]
      print(columns)
      for i in range(len(df)):
         if "yes" in  df.loc[i][columns[10]].lower():
            Event.objects.create(contact_mail=df.loc[i][columns[0]],category_id=lst[df.loc[i][columns[1]]], category=df.loc[i][columns[1]],
                                 name=df.loc[i][columns[2]].upper(), short_description=df.loc[i][columns[3]], description=df.loc[i][columns[4]],
                                 rules=df.loc[i][columns[5]], max_reg=df.loc[i][columns[6]], day=df.loc[i][columns[7]], pay=df.loc[i][columns[9]],
                                 team_event=True, team_min=df.loc[i][columns[11]], team_max=df.loc[i][columns[12]],selection="First come first serve",
                                 upload=False,name_of_incharge1=df.loc[i][columns[15]], phone_of_incharge1=df.loc[i][columns[16]],
                                 name_of_incharge2=df.loc[i][columns[17]], phone_of_incharge2=df.loc[i][columns[18]],
                                 name_of_incharge3=df.loc[i][columns[19]], phone_of_incharge3=df.loc[i][columns[20]],
                                 time_of_event=df.loc[i][columns[22]],duration_in_hours=df.loc[i][columns[23]],venue=df.loc[i][columns[24]],
                                 prize=df.loc[i][columns[26]])
         else:
            Event.objects.create(contact_mail=df.loc[i][columns[0]],category_id=lst[df.loc[i][columns[1]]], category=df.loc[i][columns[1]],
                                 name=df.loc[i][columns[2]].upper(), short_description=df.loc[i][columns[3]], description=df.loc[i][columns[4]],
                                 rules=df.loc[i][columns[5]], max_reg=df.loc[i][columns[6]], day=df.loc[i][columns[7]], pay=df.loc[i][columns[9]],
                                 team_event=False, team_min=df.loc[i][columns[11]], team_max=df.loc[i][columns[12]],selection="First come first serve",
                                 upload=False,name_of_incharge1=df.loc[i][columns[15]], phone_of_incharge1=df.loc[i][columns[16]],
                                 name_of_incharge2=df.loc[i][columns[17]], phone_of_incharge2=df.loc[i][columns[18]],
                                 name_of_incharge3=df.loc[i][columns[19]], phone_of_incharge3=df.loc[i][columns[20]],
                                 time_of_event=df.loc[i][columns[22]],duration_in_hours=df.loc[i][columns[23]],venue=df.loc[i][columns[24]],
                                 prize=df.loc[i][columns[26]])
      return Response({"message":"Success"})
   except Exception as e:
      print(e)
      return Response({"message":str(e)})
   
   # id = models.IntegerField(primary_key=True)
   #  name = models.CharField(max_length=100)
   #  category_id = models.IntegerField()
   #  category = models.CharField(max_length=100)
   #  description = models.CharField(max_length=1000, default="")
   #  short_description = models.CharField(max_length=500, default="")
   #  image_url = models.CharField(max_length=1000, default="")
   #  selection_procedure = models.CharField(max_length=100, default="")
   #  name_of_incharge1 = models.CharField(max_length=100, default="")
   #  phone_of_incharge1 = models.CharField(max_length=100, default="")
   #  name_of_incharge2 = models.CharField(max_length=100, default="")
   #  phone_of_incharge2 = models.CharField(max_length=100, default="")
   #  name_of_incharge3 = models.CharField(max_length=100, default="")
   #  phone_of_incharge3 = models.CharField(max_length=100, default="")
   #  contact_mail= models.CharField(max_length=100, default="")
   #  prize = models.CharField(default="", max_length=100)
   #  time_of_event = models.CharField(max_length=50, default="")
   #  duration_in_hours = models.CharField(max_length=5, default="")
   #  venue = models.CharField(max_length=50, default="")
   #  name_of_hosting_club = models.CharField(max_length=100, default="")
   #  rules = models.CharField(max_length=5000)
   #  selection = models.CharField(max_length=50, default="")
   #  team_event = models.BooleanField(default=False)
   #  team_min = models.IntegerField(default=0)
   #  team_max = models.IntegerField(default=0)
   #  pay = models.IntegerField(default=0)
   #  max_reg = models.IntegerField(default=10**9)
   #  upload = models.BooleanField(default=False)
   #  day = models.IntegerField(default=1)
   #  registrations = models.IntegerField(default=0)

def export_users(request):
    # Generate CSV data
   x=request.GET["key"]
   if x!="yeh_mera_secret_key_hain_tujhe_nahi_bataunga":
      return HttpResponse("Invalid Key")
   data = User.objects.values()
    
    # Set the response headers to indicate that it's a CSV file
   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = 'attachment; filename="users.csv"'
   
   # Create a CSV writer and write your data to it
   writer = csv.writer(response)
   writer.writerow(["id","name", "regno","year", "mail","mobile no", "department","college", "token", "verified"])
   # writer.writerow(['Name', 'Age'])
   for item in data:
      writer.writerow([str(item[i]) for i in item if i!="password"])
   
   return response


def export_mainevent(request):
    # Generate CSV data
   x=request.GET["key"]
   if x!="yeh_mera_secret_key_hain_tujhe_nahi_bataunga":
      return HttpResponse("Invalid Key")
   data = MainEvent.objects.values()
    
    # Set the response headers to indicate that it's a CSV file
   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = 'attachment; filename="MainEventRegister.csv"'
   
   # Create a CSV writer and write your data to it
   writer = csv.writer(response)
   writer.writerow(["id","email", "day1","day2", "day3", "combo","day1scan", "day2scan", "day3scan","day1Image", "day2Image", "day3Image","premium1", "premium2", "premium3"])
   # writer.writerow(['Name', 'Age'])
   for item in data:
      writer.writerow([str(item[i]) for i in item])
   
   return response


@api_view(['GET'])
def register_data(request):
    # Generate CSV data
   data = MainEvent.objects.values()
   s=""
   c=0
   print(data)
   for i in data:
      s+=i["email"]
      c+=1
   rec_count = s.count("@rajalakshmi.edu.in")
   rit_count = s.count("@ritchennai.edu.in")
   rsb_count = s.count("@rsb.edu.in")
   return Response({"Total":c,"rec_count":rec_count, "rit_count":rit_count, "rsb_count":rsb_count,"other_colleg":c-rec_count-rit_count-rsb_count })


@api_view(['GET'])
def eventregistrations(request):
   try:
      return Response(Event.objects.all().values("id", "name", "registrations", "day"))
   except Exception as e:
      return Response({"message":"Failure"})


@api_view(['GET'])
def makepayment(request):
   try:
      data=request.query_params
      payment_id=data["payment_id"]
      Transaction.objects.filter(payment_id=payment_id).delete()
      return Response({"message":"Success"})
   except Exception as e:
      return Response({"message":"Failure"})

def export_event(request):
    # Generate CSV data
   try:
      x=request.GET["key"]
      id=request.GET["id"]
      if x!="keep_it_a_secret":
         return HttpResponse("Invalid Key")
      data = EventRegister.objects.filter(event_id=id, paid=True).values()
      
      # Set the response headers to indicate that it's a CSV file
      response = HttpResponse(content_type='text/csv')
      response['Content-Disposition'] = f'attachment; filename="Event{id}Register.csv"'
      
      # Create a CSV writer and write your data to it
      writer = csv.writer(response)
      writer.writerow(["id","email", "eventid","teamname", "teammates", "upload","paythere", "paid"])
      # writer.writerow(['Name', 'Age'])
      for item in data:
         writer.writerow([str(item[i]) for i in item])
      
      return response
   except:
      return HttpResponse("Error")


def export_event_users(request):
    # Generate CSV data
   try:
      x=request.GET["key"]
      id=request.GET["id"]
      if x!="keep_it_a_secret":
         return HttpResponse("Invalid Key")
      data = EventRegister.objects.filter(event_id=id, paid=True).values()
      data1=[]
      for i in data:
         x=User.objects.filter(email=i["email"]).values()
         data1.extend(x)
      # Set the response headers to indicate that it's a CSV file
      response = HttpResponse(content_type='text/csv')
      response['Content-Disposition'] = f'attachment; filename="Event{id}UserDetail.csv"'
      
      # Create a CSV writer and write your data to it
      writer = csv.writer(response)
      writer.writerow(["id","name", "regno","year", "mail", "mobile no","department","college", "token", "verified"])
      # writer.writerow(['Name', 'Age'])
      for item in data1:
         writer.writerow([str(item[i]) for i in item if i!="password"])
      
      return response
   except Exception as e:
      print(e)
      return HttpResponse("Error"+str(e))


@api_view(['GET'])
def qrcodeverify(request):
   try:
      today = date.today()
      data=request.query_params
      email = data["email"]
      day = data["day"]
      m=MainEvent.objects.get(email=email)
      if day=="1":
         m.day1Scan = 1
      elif day=="2":
         m.day2Scan = 1
      elif day=="3":
         m.day3Scan = 1
      m.save()
      return Response({"message":"Verified"})
   except Exception as e:
      print(e)
      return Response({"message":"Ask the data administrator to verify. There is some problem I guess"})


def maineventdata(request):
    # Generate CSV data
   x=request.GET["key"]
   if x!="yeh_mera_secret_key_hain_tujhe_nahi_bataunga":
      return HttpResponse("Invalid Key")
   data = MainEvent.objects.values()
   # cursor = connection.cursor()    
   # cursor.execute('''select * from User u, MainEvent m where u.email=m.email ''')
   # row = cursor.fetchall()
   # print(row)

   d=[]
   for i in data:
      x={}
      u= User.objects.filter(email=i["email"]).values()
      for j in u[0]:
         if j!='password' and j!='id':
            x[j]=u[0][j]
      for j in i:
         if j!='email':
            x[j]=i[j]
      d.append(x)
   # print(d)

    
    # Set the response headers to indicate that it's a CSV file
   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = 'attachment; filename="MainEventRegister.csv"'
   
   # Create a CSV writer and write your data to it
   writer = csv.writer(response)
   writer.writerow(["name", "regno", "year", "email", "mobile no","dept", "collegename", "token", "is_verified","id", "day1","day2", "day3", "combo","day1scan", "day2scan", "day3scan","day1Image", "day2Image", "day3Image","premium1", "premium2", "premium3"])
   # writer.writerow(['Name', 'Age'])
   for item in d:
      writer.writerow([str(item[i]) for i in item])
   
   return response


@api_view(['GET'])
def scans(request):
   try:
      d={}
      d["day1"]=len(MainEvent.objects.filter(day1Scan=1).values())
      d["day2"]=len(MainEvent.objects.filter(day2Scan=1).values())
      d["day3"]=len(MainEvent.objects.filter(day3Scan=1).values())
      return Response(d)
   except:
      return Response({"message":"failure"})
