from django.shortcuts import render, redirect, HttpResponse
from tickets.models import User, Event, MainEvent, EventRegister,TeamMates, ForgotPassword, PremimumTicket, Transaction, Merch
import datetime, jwt
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.urls import reverse
import qrcode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.hashers import check_password
from email import encoders
from email.mime.image import MIMEImage
from . import instamojo_api
import urllib.request
import os
from PIL import Image
import traceback  

url="localhost:8000"

def logout(request):
    try:
        response = redirect("login")
        response.delete_cookie('jwt')
        return response
    except Exception as e:
        print(e)
        return HttpResponse("Some error occurred")


def send_mail_func(email, path, path_ticket, day, t=False):
    u=User.objects.filter(email=email)
    name=u[0].name
    if t:
        s=f'''Dear {name}, \nThank you for purchasing your Proshow pass for Recharge 2023. We are super excited for you to witness the biggest cultural extravaganza of the season. So get ready to reignite, rejuvenate and revivify the REC way! Until then, stay charged.\n\n1. Participants of Recharge 2023 must carry their institution’s ID along with any of their government issued ID cards on the days of the fest (Aadhaar Card / PAN Card / Driving License, etc.)
2. Participants are required to have their registration QR codes with them at all times.
3. Participants must wear their wristband at all times during the day and can only take it off after the conclusion of the proshow events.
4. Participants are prohibited from bringing alcohol, cigarettes and other narcotic substances to the fest. If found, the person will be evicted from the fest immediately and their passes will be canceled.
5. The Management is not responsible for any loss of personal belongings of the participants.\n\n Please find the Premium ticket for Day {day}\n\nRegards,\nTeam Recharge'''
    else:
        s=f'''Dear {name}, \nThank you for purchasing your Proshow pass for Recharge 2023. We are super excited for you to witness the biggest cultural extravaganza of the season. So get ready to reignite, rejuvenate and revivify the REC way! Until then, stay charged.\n\n1. Participants of Recharge 2023 must carry their institution’s ID along with any of their government issued ID cards on the days of the fest (Aadhaar Card / PAN Card / Driving License, etc.)
2. Participants are required to have their registration QR codes with them at all times.
3. Participants must wear their wristband at all times during the day and can only take it off after the conclusion of the proshow events.
4. Participants are prohibited from bringing alcohol, cigarettes and other narcotic substances to the fest. If found, the person will be evicted from the fest immediately and their passes will be canceled.
5. The Management is not responsible for any loss of personal belongings of the participants.\n\n Please find the ticket for Day {day}\n\nRegards,\nTeam Recharge'''
    emailsend = EmailMessage(
    f'Ticket for Day {day}', 
    s, 
    settings.EMAIL_HOST_USER, 
    [email]
    )
    with open(path, 'rb') as f:
        emailsend.attach(f'day{day}qrcode.png', f.read())
    # with open(path_ticket, 'rb') as f:
    #     emailsend.attach(f'day{day}ticket.png', f.read())
    # try:
    #     os.remove(path_ticket)
    # except:
    #     pass
    emailsend.send()

def forgot_password_verification(request):
    try:
        token = request.GET.get('token')
        email = request.GET.get('email')
        if not token:
            return HttpResponse('<h1>Verification Failed</h1>')
        temp = ForgotPassword.objects.get(email=email)

        if not temp:
            return HttpResponse('<h1>No such mail id exists</h1>')

        if temp.token != token:
            return HttpResponse('<h1>Verification Failed</h1>')
        change = User.objects.get(email=email, is_verified=True)

        change.password = temp.password
        change.save()

        # return HttpResponse('<h1>Password Changed Successfully. Abe saale iske baad password bhulna mat </h1>')
        return redirect("login")
    except:
        return HttpResponse("<h1>Verification Failed</h1>")

def verify_email(request):
    try:
        token = request.GET.get('token')
        email = request.GET.get('email')
        if not token:
            return HttpResponse('<h1>Verification Failed</h1>')
        temp = User.objects.get(email=email)

        if not temp:
            return HttpResponse('<h1>Verification Failed</h1>')
        
        if temp.is_verified:
            return HttpResponse("<h1>Already Verified</h1>")

        if temp.token != token:
            return HttpResponse('<h1>Verification Failed</h1>')

        temp.is_verified = True
        temp.save()

        # return HttpResponse('<h1>Successfully Verified Mail Now you can go login and go to the app</h1>')
        return redirect("login")
    except:
        return HttpResponse('<h1>Verification Failed</h1>')
# Create your views here.
def register(request):
    try:
        d={}
        d["name"]=""
        d["regno"]=""
        d["year"]=""
        d["dept"]=""
        d["email"]=""
        d["password"]=""
        d["phoneno"]=""
        d["college"]=""
        d["confirmpassword"]=""
        d["show"]=0
        d["message"]=""
        if request.method=="POST":
            name = request.POST.get("name").strip()
            regno = request.POST.get("regno").strip()
            year = request.POST.get("year").strip()
            dept = request.POST.get("dept").strip()
            email = request.POST.get("email").strip().lower()
            phoneno = request.POST.get("phoneno").strip()
            password = request.POST.get("password").strip()
            college = request.POST.get("college").strip()
            confirmpassword = request.POST.get("confirmpassword").strip()
            d["name"]=name
            d["regno"]=regno
            d["year"]=year
            d["dept"]=dept
            d["email"]=email
            d["password"]=password
            d["college"]=college
            d["confirmpassword"]=confirmpassword
            d["phoneno"]=phoneno
            d["message"]=""
            temp = User.objects.filter(email=email)
            message=None
            if password and  len(password)<8:
                message="Password length should be greater than 8"
            elif not name or not regno or not year or not dept or not email or not password or not college:
                message="Please fill all the fields"
            elif len(name)>50 or len(regno)>50 or len(year)>10 or len(dept)>=100 or len(email)>200 or len(password)>20 or len(college)>=100:
                message="Field lengths should not cross the limit"
            elif password!=confirmpassword:
                message="Password does not match confirm password"
            d["message"]=message
            if message:
                return render(request, "register.html", d)
            temp = User.objects.filter(email=email)
            if temp:
                d["show"]=1
                return render(request, "register.html",d)
            verification_token = get_random_string(length=32)
            verification_url = request.build_absolute_uri(reverse('verify_email')) + f'?token={verification_token}&email={email}'
            User.objects.create(name=name, regno=regno, dept=dept,email=email,collegename=college,phoneno=phoneno,
            year=year, password=password, token=verification_token, is_verified=False)
            send_mail(
                'Verify your email',
                f'You have successfully created an account. Click this link to verify your email: {verification_url}\n\nRegards,\nTeam Recharge',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            
            return redirect("login")
        return render(request, "register.html",d)
    except:
        return HttpResponse("<h1>Unexpected Error</h1>")


def forgotpassword(request):
    try:
        d={}
        d["email"]=""
        d["password"]=""
        d["confirmpassword"]=""
        d["message"]=""
        d["show"]=0
        if request.method=="POST":
            email = request.POST.get("email").strip().lower()
            password = request.POST.get("password").strip()
            confirmpassword = request.POST.get("confirmpassword").strip()
            d["email"]=email
            d["password"]=password
            d["confirmpassword"]=confirmpassword
            temp = User.objects.filter(email=email, is_verified=True)
            message=None
            if password and  len(password)<8:
                message="Password length should be greater than or equal to 8"
            elif password and len(password)>20:
                message="Password length should be less than 20"
            elif not email or not password or not confirmpassword:
                message="Please fill all the fields"
            elif password!=confirmpassword:
                message="Password does not match confirm password"
            d["message"]=message
            if message:
                return render(request, "forgotpassword.html", d)
            if temp is None:
                d["show"]=1
                return render(request, "forgotpassword.html", d)
            
            verification_token = get_random_string(length=32)
            verification_url = request.build_absolute_uri(reverse('forgot_password_verification')) + f'?token={verification_token}&email={email}'

            send_mail(
                'Change Password',
                f'Click on this link to Change your password: {verification_url}\n\nRegards,\nTeam Recharge',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            if not ForgotPassword.objects.filter(email=email):
                ForgotPassword.objects.create(email=email, password=password, token=verification_token)
            else:
                f=ForgotPassword.objects.get(email=email)
                f.token=verification_token
                f.password=password
                f.save()
            
            return redirect("login")
        return render(request, "forgotpassword.html",d)
    except:
        return HttpResponse("<h1>Unexpected Error</h1>")

def login(request):
    try:
        d={}
        d["email"]=""
        d["password"]=""
        d["show"]=0
        if request.method=="POST":
            email=request.POST.get("email").strip().lower()
            password = request.POST.get("password").strip()
            d["email"]=email
            d["password"]=password
            temp = User.objects.filter(email=email, is_verified=True)
            if temp:
                if check_password(password, temp[0].password):
                    payload = {
                        'id':email,
                        'exp':datetime.datetime.utcnow() + datetime.timedelta(days=60),
                        'iat':datetime.datetime.utcnow()
                    }

                    token = jwt.encode(payload, 'gahih1h26*&&^@^*GHhduhau^&^*782hgh*&^&^&ghdghay^&^&^*&ghdghag87^&^&ghdsa876738gh78t78GYUT^6736gyd6756^&TYGT6738827y7gh*&&^%^&&^%&*hhdyiasudhikhsakhGHGHDGHSGKGKHgyudgyushjhgjGDhGSHDg*^%*^^&^&now_you_decode_ra', algorithm='HS256')
                    response = redirect("test")

                    response.set_cookie(key='jwt', value=token, httponly=True)
                    
                    return response
                else:
                    d["show"]=2
                    return render(request,"login.html", d)

            else:
                d["show"]=1
                return render(request,"login.html", d)

            
        return render(request,"login.html", d)
    except Exception as e:
        print(traceback.exc())
        return HttpResponse("<h1>Unexpected Error</h1>")
    
def test(request):
    try:
        token = request.COOKIES.get('jwt')
        if not token:
            print(token)
            return redirect("login")
        
        try:
            payload = jwt.decode(token, 'gahih1h26*&&^@^*GHhduhau^&^*782hgh*&^&^&ghdghay^&^&^*&ghdghag87^&^&ghdsa876738gh78t78GYUT^6736gyd6756^&TYGT6738827y7gh*&&^%^&&^%&*hhdyiasudhikhsakhGHGHDGHSGKGKHgyudgyushjhgjGDhGSHDg*^%*^^&^&now_you_decode_ra', 'HS256')
        except jwt.ExpiredSignatureError as e:
            print(traceback.exc())
            return redirect("login")
        temp=payload['id']
        temp1 = User.objects.filter(email=temp)
        d={}
        d["name"]=temp1[0].name
        x=MainEvent.objects.filter(email=temp)
        if x:
            d["day1"]=x[0].day1
            d["day2"]=x[0].day2
            d["day3"]=x[0].day3
            d["premium1"]=x[0].premium1
            d["premium2"]=x[0].premium2
            d["premium3"]=x[0].premium3
        else:
            d["day1"]=False
            d["day2"]=False
            d["day3"]=False
            d["premium1"]=False
            d["premium2"]=False
            d["premium3"]=False
        if temp[-19:]=="@rajalakshmi.edu.in" or temp[-18:]=="@ritchennai.edu.in" or temp[-11:]=="rsb.edu.in":
            d["show"]=not d["premium1"] or not d['premium2'] or not d["premium3"]
        else:
            d["show"]=not d["day1"] or not d["day2"] or not d["day3"]
        x=EventRegister.objects.filter(email=temp, paid=True)
        lst=set()
        for i in x:
            lst.add(i.event_id)
        x=TeamMates.objects.filter(team_mate=temp, verified=True)
        for i in x:
            lst.add(i.event_id)
        events=[]
        for i in lst:
            x=Event.objects.filter(id=i)
            events.append(x[0].name)
        d["day1_events"] = []
        d["day2_events"]=[]
        d["day3_events"]=[]
        if d["day2"]:
            d["day2_events"]=Event.objects.filter(day=2)
        if d['day3']:
            d["day3_events"]=Event.objects.filter(day=3)

        d["events"]=events
        d["eventslist"] = Event.objects.all()
        d["merch"]=len(Merch.objects.filter(email=temp).values())
        print(d)
        return render(request, "test.html",d)
    except Exception as e:
        print(traceback.exc())
        return HttpResponse("<h1>Unexpected Error</h1>")

def resendmail(request):
    try:
        d={}
        d["email"]=""
        d["show"]=0
        if request.method=="POST":
            email=request.POST.get("email").strip().lower()
            d["email"]=email
            temp = User.objects.filter(email=email, is_verified=False)
            if not temp:
                d["show"]=1
                return render(request,"resendmail.html", d)
            verification_token = get_random_string(length=32)
            verification_url = request.build_absolute_uri(reverse('verify_email')) + f'?token={verification_token}&email={email}'

            send_mail(
                'Verify your email',
                f'Click on this link to verify your email: {verification_url}\n\nRegards,\nTeam Recharge',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True,
            )
            u = User.objects.get(email=email, is_verified=False)
            u.token=verification_token
            u.save()
            return redirect("login")
        return render(request,"resendmail.html", d)
    except:
        return HttpResponse("<h1>Unexpected Error</h1>")

def event(request, id):
    try:
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect("login")
        
        try:
            payload = jwt.decode(token, 'gahih1h26*&&^@^*GHhduhau^&^*782hgh*&^&^&ghdghay^&^&^*&ghdghag87^&^&ghdsa876738gh78t78GYUT^6736gyd6756^&TYGT6738827y7gh*&&^%^&&^%&*hhdyiasudhikhsakhGHGHDGHSGKGKHgyudgyushjhgjGDhGSHDg*^%*^^&^&now_you_decode_ra', 'HS256')
        except jwt.ExpiredSignatureError:
            return redirect("login")
        email=payload['id']
        if not id.isnumeric() or int(id)>70:
            return HttpResponse("<h1>No such url exists</h1>")
        d={}
        temp = Event.objects.filter(id=id)[0]
        check = EventRegister.objects.filter(event_id=int(id), email=email, paid=True)
        check1 = TeamMates.objects.filter(event_id=int(id), team_mate=email, verified=True)
        if check or check1:
            d["already_registered"]=True
        else:
            d["already_registered"]=False
        if email[-19:]=="@rajalakshmi.edu.in" or email[-18:]=="@ritchennai.edu.in" or email[-11:]=="@rsb.edu.in":
            d["has_ticket"]=False
        x=MainEvent.objects.filter(email=email)
        if x:
            if (temp.day==1 and x[0].day1) or (temp.day==2 and x[0].day2) or (temp.day==3 and x[0].day3):
                d["has_ticket"]=True
            else:
                d["has_ticket"]=False
        else:
            d["has_ticket"]=False
        d["id"]=temp.id
        d["name"]=temp.name
        d["category"]=temp.category
        d["rules"]="- "+temp.rules.strip().replace("\n", "\n\n- ")
        d["pay"]=temp.pay
        d["description"]=temp.description
        d["team_event"]=temp.team_event
        d["registrations"]=temp.registrations
        d["max_reg"]=temp.max_reg
        d["team_min"]=temp.team_min
        d["team_max"]=temp.team_max
        d["upload"]=temp.upload
        d["day"]=temp.day
        d["lst"]=range(1,d["team_max"])
        d["show"]=False
        d["message"]=""
        d["show1"]=False
        d["register_there"]=True
        if d["pay"]==-1:
            d["register_there"]=False
        
        if request.method=="POST":
            if d["team_event"]:
                team_mates=""
                team_name = request.POST.get("teamName")
                if not team_name:
                    d["message"]="Please enter the team name"
                    return render(request, "event_register.html", d)
                count=1
                for i in range(1, d["team_max"]):
                    temail = request.POST.get("teamMatesMailId"+str(i))
                    if not temail:
                        continue
                    temail=temail.strip().lower()
                    print(temail)
                    if temail=="":
                        continue
                    if temail==email:
                        d["message"]="Can't enter your mail id itself in team mate mail id"
                        return render(request, "event_register.html", d)
                    elif temail in team_mates:
                        d["message"]="Team Mate unique mail id should be there"
                        return render(request, "event_register.html", d)
                    
                    if False:
                        if User.objects.filter(email=temail, is_verified=True):
                            pass
                        else:
                            d["show"]=True
                            return render(request, "event_register.html", d)
                    else:
                        if d["day"]==1:
                            t = MainEvent.objects.filter(email=temail, day1=True)
                            if not t:
                                d["show"]=True
                                return render(request, "event_register.html", d)
                        if d["day"]==2:
                            t = MainEvent.objects.filter(email=temail, day2=True)
                            if not t:
                                d["show"]=True
                                return render(request, "event_register.html", d)
                        if d["day"]==3:
                            t = MainEvent.objects.filter(email=temail, day3=True)
                            if not t:
                                d["show"]=True
                                return render(request, "event_register.html", d)
                    if TeamMates.objects.filter(team_mate=temail, event_id=d["id"], verified=True):
                        d["message"]=temail+" has already been registered in another team"
                        return render(request, "event_register.html", d)
                    team_mates+=temail+","
                    # print(count, "incremented")
                    count+=1
                # print(team_mates, count)
                if d["team_min"]>count:
                    d["show1"]=d["team_min"]-1

                    return render(request, "event_register.html", d)
                if d["upload"]:
                    upload=request.POST.get("upload")
                    if not upload:
                        d["message"]="Please upload the file and attach its drive link"
                        return render(request, "event_register.html", d)
                    if d["pay"]!=0:
                        if not EventRegister.objects.filter(email=email,event_id=d["id"]):
                            y=EventRegister(email=email, team_name=team_name, team_mates=team_mates[:-1], upload_link=upload, event_id=d["id"], pay_there=True)
                            y.save()
                            z=EventRegister.objects.filter(email=email, event_id=d["id"])
                            teamMate = TeamMates(team_mate=email, event_register_id=z[0].id,event_id=d["id"], verified=False)
                            teamMate.save()
                            for i in team_mates[:-1].split(","):
                                if i.strip()!="":
                                    teamMate = TeamMates(team_mate=i, event_register_id=z[0].id,event_id=d["id"], verified=False)
                                    teamMate.save()
                            amount = d["pay"]
                            purpose = f"Event {d['id']} Registration"
                        else:
                            y=EventRegister.objects.get(email=email,event_id=d["id"])
                            y.team_name=team_name
                            y.team_mates=team_mates[:-1]
                            y.upload_link=upload
                            y.save()
                            z=EventRegister.objects.filter(email=email, event_id=d["id"])
                            TeamMates.objects.filter(event_register_id=z[0].id).delete()
                            teamMate = TeamMates(team_mate=email, event_register_id=z[0].id,event_id=d["id"], verified=False)
                            teamMate.save()
                            for i in team_mates[:-1].split(","):
                                if i.strip()!="":
                                    teamMate = TeamMates(team_mate=i, event_register_id=z[0].id,event_id=d["id"], verified=False)
                                    teamMate.save()
                        amount = d["pay"]
                        purpose = f"Event {d['id']} Registration"

                        # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
                        payment_url = instamojo_api.payment_request(email, amount, purpose)
                        if payment_url is None:
                            return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
                        return redirect(payment_url)
                    else:
                        y=EventRegister(email=email, team_name=team_name, team_mates=team_mates[:-1], upload_link=upload, event_id=d["id"], paid=True)
                        y.save()
                    z=EventRegister.objects.filter(email=email, event_id=d["id"])
                    teamMate = TeamMates(team_mate=email, event_register_id=z[0].id,event_id=d["id"], verified=True)
                    teamMate.save()
                    for i in team_mates[:-1].split(","):
                        if i.strip()!="":
                            teamMate = TeamMates(team_mate=i, event_register_id=z[0].id,event_id=d["id"], verified=True)
                            teamMate.save()
                    z=Event.objects.get(id=d["id"])
                    z.registrations = z.registrations+1
                    z.save()
                    return redirect("test")
                else:
                    if d["pay"]!=0:
                        if not EventRegister.objects.filter(email=email,event_id=d["id"]):
                            y=EventRegister(email=email, team_name=team_name, team_mates=team_mates[:-1], event_id=d["id"], pay_there=True)
                            y.save()
                            z=EventRegister.objects.filter(email=email, event_id=d["id"])
                            teamMate = TeamMates(team_mate=email, event_register_id=z[0].id,event_id=d["id"], verified=False)
                            teamMate.save()
                            for i in team_mates[:-1].split(","):
                                if i.strip()!="":
                                    teamMate = TeamMates(team_mate=i, event_register_id=z[0].id,event_id=d["id"], verified=False)
                                    teamMate.save()
                        else:
                            y=EventRegister.objects.get(email=email,event_id=d["id"])
                            y.team_name=team_name
                            y.team_mates=team_mates[:-1]
                            y.save()
                            z=EventRegister.objects.filter(email=email, event_id=d["id"])
                            TeamMates.objects.filter(event_register_id=z[0].id).delete()
                            teamMate = TeamMates(team_mate=email, event_register_id=z[0].id,event_id=d["id"], verified=False)
                            teamMate.save()
                            for i in team_mates[:-1].split(","):
                                if i.strip()!="":
                                    teamMate = TeamMates(team_mate=i, event_register_id=z[0].id,event_id=d["id"], verified=False)
                                    teamMate.save()
                        amount = d["pay"]
                        purpose = f"Event {d['id']} Registration"

                        # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
                        payment_url = instamojo_api.payment_request(email, amount, purpose)
                        if payment_url is None:
                            return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
                        return redirect(payment_url)
                    else:
                        y=EventRegister(email=email, team_name=team_name, team_mates=team_mates[:-1], event_id=d["id"], paid=True)
                        y.save()
                    z=EventRegister.objects.filter(email=email, event_id=d["id"])
                    teamMate = TeamMates(team_mate=email, event_register_id=z[0].id,event_id=d["id"], verified=True)
                    teamMate.save()
                    for i in team_mates[:-1].split(","):
                        if i.strip()!="":
                            teamMate = TeamMates(team_mate=i, event_register_id=z[0].id,event_id=d["id"], verified=True)
                            teamMate.save()
                    z=Event.objects.get(id=d["id"])
                    z.registrations = z.registrations+1
                    z.save()
                    return redirect("test")
            else:
                if d["upload"]:
                    upload=request.POST.get("upload")
                    if not upload:
                        d["message"]="Please upload the file and attach its drive link"
                        return render(request, "event_register.html", d)
                    if d["pay"]!=0:
                        y=EventRegister(email=email, upload_link=upload, event_id=d["id"], pay_there=True)
                        y.save()
                        amount = d["pay"]
                        purpose = f"Event {d['id']} Registration"

                        # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
                        payment_url = instamojo_api.payment_request(email, amount, purpose)
                        if payment_url is None:
                            return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
                        return redirect(payment_url)
                    else:
                        y=EventRegister(email=email, upload_link=upload, event_id=d["id"], paid=True)
                        y.save()
                    z=Event.objects.get(id=d["id"])
                    z.registrations = z.registrations+1
                    z.save()
                    return redirect("test")
                else:
                    if d["pay"]!=0:
                        if not EventRegister.objects.filter(email=email, event_id=d["id"]):
                            y=EventRegister(email=email,  event_id=d["id"], pay_there=True)
                            y.save()
                        amount = d["pay"]
                        purpose = f"Event {d['id']} Registration"

                        # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
                        payment_url = instamojo_api.payment_request(email, amount, purpose)
                        if payment_url is None:
                            return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
                        return redirect(payment_url)
                    else:
                        y=EventRegister(email=email,  event_id=d["id"], paid=True)
                        y.save()
                    z=Event.objects.get(id=d["id"])
                    z.registrations = z.registrations+1
                    z.save()
                    return redirect("test")
            



        print(d)
        return render(request, "event_register.html", d)
    except Exception as e:
        return HttpResponse(f"<h1>Unexpected Error {e}</h1>")

def mainevent(request):
    try:
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect("login")
        
        try:
            payload = jwt.decode(token, 'gahih1h26*&&^@^*GHhduhau^&^*782hgh*&^&^&ghdghay^&^&^*&ghdghag87^&^&ghdsa876738gh78t78GYUT^6736gyd6756^&TYGT6738827y7gh*&&^%^&&^%&*hhdyiasudhikhsakhGHGHDGHSGKGKHgyudgyushjhgjGDhGSHDg*^%*^^&^&now_you_decode_ra', 'HS256')
        except jwt.ExpiredSignatureError:
            return redirect("login")
        email=payload['id']
        rec=False
        if email[-19:]=="@rajalakshmi.edu.in" or email[-18:]=="@ritchennai.edu.in" or email[-11:]=="@rsb.edu.in":
            # return HttpResponse("<h1>REC Students no need to buy tickets for the Main Event</h1>")
            rec=True
        if request.method=="POST":
            if rec:
                m=MainEvent.objects.filter(email=email)
                if not m:
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    data = email+"day1"+get_random_string(length=8)
                    qr.add_data(data)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    path1 = r"static/tickets/"+data+".png"
                    img.save(path1)
                    # print("Some error")
                    img2 = Image.open(path1)
                    # print("Some error")
                    new_image = img2.resize((274, 272))
                    new_image.save(path1)
                    # print("Some error")
                    path_ticket1 = r"static/main_ticket/"+data+".png"
                    img1 = Image.open(r"static/ticket_template/day1_standard.png")
                    img2 = Image.open(path1)
                    img1.paste(img2, (80, 160), mask=img2)
                    img1.save(path_ticket1)
                    

                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    data = email+"day2"+get_random_string(length=8)
                    qr.add_data(data)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    path2 = r"static/tickets/"+data+".png"
                    img.save(path2)
                    img2 = Image.open(path2)
                    new_image = img2.resize((274, 272))
                    new_image.save(path2)
                    path_ticket2 = r"static/main_ticket/"+data+".png"
                    img1 = Image.open(r"static/ticket_template/day2_standard.png")
                    img2 = Image.open(path2)
                    img1.paste(img2, (80, 160), mask=img2)
                    img1.save(path_ticket2)
                    m=MainEvent(email=email, day1=True, day2=True, day1Image=path1, day2Image=path2)
                    m.save()
                    send_mail_func(email=email, path=path1,path_ticket=path_ticket1, day=1)
                    send_mail_func(email=email, path=path2,path_ticket=path_ticket2, day=2)

                # qr = qrcode.QRCode(version=1, box_size=10, border=5)
                # data = email+"day3"+get_random_string(length=8)
                # qr.add_data(data)
                # qr.make(fit=True)
                # img = qr.make_image(fill_color="black", back_color="white")
                # path3 = r"static/tickets/"+data+".png"
                # img.save(path3)
                # img2 = Image.open(path3)
                # new_image = img2.resize((274, 272))
                # new_image.save(path3)
                # path_ticket3 = r"static/main_ticket/"+data+".png"
                # img1 = Image.open(r"static/ticket_template/day3_standard.png")
                # img2 = Image.open(path3)
                # img1.paste(img2, (80, 160), mask=img2)
                # img1.save(path_ticket3)
                # send_mail_func(email=email, path=path3,path_ticket=path_ticket3, day=3)
                
                return redirect("test")
            d={}
            d["invalid"]=False
            day=request.POST.get("day")
            if not day or not day.isnumeric() or int(day)>2:
                d["invalid"]=True
                x=MainEvent.objects.filter(email=email)
                if x:
                    d["day1"]=not x[0].day1
                    d["day2"]=not x[0].day2
                else:
                    d["day1"]=True
                    d["day2"]=True
                d["rec"]=rec
                d["show"]=True
                return render(request, "mainevent_register.html", d)
            x=MainEvent.objects.filter(email=email)
            if x:
                m = MainEvent.objects.get(email=email)
            day=int(day)
            if x:
                d["day1"]=not x[0].day1
                d["day2"]=not x[0].day2
                d["day3"]=not x[0].day3
            else:
                d["day1"]=True
                d["day2"]=True
                d["day3"]=True
            d["rec"]=rec
            if day==1 and d["day1"]:
                if rec:
                    # amount = 750
                    # purpose = 'Day 1 Ticket'

                    # # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
                    # payment_url = instamojo_api.payment_request(email, amount, purpose)
                    # if payment_url is None:
                    #     return HttpResponse("<h1>Koi error agaya re sorry yaar</h1>")
                    # return redirect(payment_url)
                    return HttpResponse("<h1>No normal Day 1 Ticket for REC students</h1>")
                else:
                    # amount = 775
                    amount = 10
                    purpose = 'Day 1 Ticket'

                    # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
                    payment_url = instamojo_api.payment_request(email, amount, purpose)
                    if payment_url is None:
                        return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
                    return redirect(payment_url)
            elif day==2 and d["day2"]:
                if rec:
                    # amount = 750
                    # purpose = 'Day 2 Ticket'

                    # # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
                    # payment_url = instamojo_api.payment_request(email, amount, purpose)
                    # if payment_url is None:
                    #     return HttpResponse("<h1>Koi error agaya re sorry yaar</h1>")
                    # return redirect(payment_url)
                    return HttpResponse("<h1>No normal Day 2 Ticket for REC students</h1>")
                else:
                    # amount = 7s75
                    amount = 10
                    purpose = 'Day 2 Ticket'

                    # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
                    payment_url = instamojo_api.payment_request(email, amount, purpose)
                    if payment_url is None:
                        return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
                    return redirect(payment_url)
            # elif day==3 and d["day3"]:
            #     if rec:
            #         # amount = 750
            #         # purpose = 'Day 3 Ticket'

            #         # # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         # payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         # if payment_url is None:
            #         #     return HttpResponse("<h1>Koi error agaya re sorry yaar</h1>")
            #         # return redirect(payment_url)
            #         return HttpResponse("<h1>No normal Day 3 Ticket for REC students</h1>")
            #     else:
            #         amount = 775
            #         # amount = 10
            #         purpose = 'Day 3 Ticket'

            #         # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         if payment_url is None:
            #             return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #         return redirect(payment_url)
            # elif day==4 and d["day1"] and d["day2"] and d["day3"]:
            #     if rec:
            #         amount = 525
            #         # amount = 10
            #         purpose = 'Combo Ticket REC'

            #         # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         if payment_url is None:
            #             return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #         return redirect(payment_url)
            #     else:
            #         amount = 1650
            #         # amount = 10
            #         purpose = 'Combo Ticket'

            #         # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         if payment_url is None:
            #             return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #         return redirect(payment_url)
            # elif day==5 :
            #     if rec:
            #         amount = 1550
            #         # amount = 10
            #         purpose = 'Fanpit Day 1 Ticket REC'

            #         # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         if payment_url is None:
            #             return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #         return redirect(payment_url)
            #     else:
            #         if d["day1"]:
            #             amount = 1550
            #             # amount = 10
            #             purpose = 'Fanpit Day 1 Ticket'

            #             # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #             payment_url = instamojo_api.payment_request(email, amount, purpose)
            #             if payment_url is None:
            #                 return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #             return redirect(payment_url)
            # elif day==6:
            #     if rec:
            #         amount = 1550
            #         # amount = 10
            #         purpose = 'Fanpit Day 2 Ticket REC'

            #         # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         if payment_url is None:
            #             return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #         return redirect(payment_url)
            #     else:
            #         if d["day2"]:
            #             amount = 1550
            #             # amount = 10
            #             purpose = 'Fanpit Day 2 Ticket'

            #             # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #             payment_url = instamojo_api.payment_request(email, amount, purpose)
            #             if payment_url is None:
            #                 return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #             return redirect(payment_url)
            # elif day==7:
            #     if rec:
            #         amount = 1550
            #         # amount = 10
            #         purpose = 'Fanpit Day 3 Ticket REC'

            #         # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         if payment_url is None:
            #             return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #         return redirect(payment_url)
            #     else:
            #         if d["day3"]:
            #             amount = 1550
            #             # amount = 10
            #             purpose = 'Fanpit Day 3 Ticket'

            #             # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #             payment_url = instamojo_api.payment_request(email, amount, purpose)
            #             if payment_url is None:
            #                 return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #             return redirect(payment_url)
            # elif day==8 and d["day1"] and d["day2"] and d["day3"]:
            #     if rec:
            #         # amount = 10
            #         # purpose = 'Fanpit Combo Ticket'

            #         # # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         # payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         # if payment_url is None:
            #         #     return HttpResponse("<h1>Koi error agaya re sorry yaar</h1>")
            #         # return redirect(payment_url)
            #         return HttpResponse("<h1>No Fanpit Combo for rec students</h1>")
            #     else:
            #         amount = 4650
            #         # amount = 10
            #         purpose = 'Fanpit Combo Ticket'

            #         # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            #         payment_url = instamojo_api.payment_request(email, amount, purpose)
            #         if payment_url is None:
            #             return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            #         return redirect(payment_url)
            
            return redirect("test")
        d={}

        x=MainEvent.objects.filter(email=email)
        if x:
            d["day1"]=not x[0].day1
            d["day2"]=not x[0].day2
            
        else:
            d["day1"]=True
            d["day2"]=True
        d["rec"]=rec
        d["show"]=True
        d["invalid"]=False
        if rec:
            if not d["day1"] and not d["day2"]:
                d["show"]=False
        else:
            if not d["day1"] and not d["day2"]:
                d["show"]=False
        print(d)
        return render(request, "mainevent_register.html", d)
    except Exception as e:
        print(traceback.exc())
        return HttpResponse("<h1>Unexpected Error</h1>")

# def premiumticket(request):
#     try:
#         d={}
#         d["message"]=""
#         d["show"]=True
#         d["day1"]=True
#         d["day2"]=True
#         d["day3"]=True
#         token = request.COOKIES.get('jwt')
#         if not token:
#             return redirect("login")
        
#         try:
#             payload = jwt.decode(token, 'gahih1h26*&&^@^*GHhduhau^&^*782hgh*&^&^&ghdghay^&^&^*&ghdghag87^&^&ghdsa876738gh78t78GYUT^6736gyd6756^&TYGT6738827y7gh*&&^%^&&^%&*hhdyiasudhikhsakhGHGHDGHSGKGKHgyudgyushjhgjGDhGSHDg*^%*^^&^&now_you_decode_ra', 'HS256')
#         except jwt.ExpiredSignatureError:
#             return redirect("login")
#         email=payload['id']
#         if request.method=="POST":
#             day=request.POST.get("day")
#             if not day or not day.isnumeric() or int(day)>3:
#                 return HttpResponse("<h1>Hack karne ki koshish mat kar be Teri Activity record ho chuki hain aur ab tu fasega. Hindi agar samajh main nahi aati toh jaakar translate kar le </h1>")
#             x=MainEvent.objects.filter(email=email)
#             day=int(day)
#             if x:
#                 if not x[0].day1:
#                     d["day1"]=False
#                 if not x[0].day2:
#                     d["day2"]=False
#                 if not x[0].day3:
#                     d["day3"]=False
#                 x = PremimumTicket.objects.filter(email=email)
#                 for i in x:
#                     if i.day==1:
#                         d["day1"]=False
#                     elif i.day==2:
#                         d["day2"]=False
#                     elif i.day==3:
#                         d["day3"]=False
#             else:
#                 d["message"]="You don't have ticket for events"
#                 d["show"]=False
#                 return render(request, "premium.html", d)
#             x = PremimumTicket.objects.filter(email=email, day=day)
#             if not x:
#                 if day==1 and d["day1"]:
#                     # PremimumTicket.objects.create(email=email, day=1)
#                     amount = 10
#                     purpose = 'Premium Day 1 Ticket'

#                     # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
#                     payment_url = instamojo_api.payment_request(email, amount, purpose)
#                     if payment_url is None:
#                         return HttpResponse("<h1>Koi error agaya re sorry yaar</h1>")
#                     return redirect(payment_url)
#                 elif day==2 and d["day2"]:
#                     # PremimumTicket.objects.create(email=email, day=2)
#                     amount = 10
#                     purpose = 'Premium Day 2 Ticket'

#                     # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
#                     payment_url = instamojo_api.payment_request(email, amount, purpose)
#                     if payment_url is None:
#                         return HttpResponse("<h1>Koi error agaya re sorry yaar</h1>")
#                     return redirect(payment_url)
#                 elif day==3 and d["day3"]:
#                     # PremimumTicket.objects.create(email=email, day=3)
#                     amount = 10
#                     purpose = 'Premium Day 3 Ticket'

#                     # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
#                     payment_url = instamojo_api.payment_request(email, amount, purpose)
#                     if payment_url is None:
                        
#                         return HttpResponse("<h1>Koi error agaya re sorry yaar</h1>")
#                     return redirect(payment_url)
#                 return redirect("test")
        
#         x=MainEvent.objects.filter(email=email)
#         if x:
#             if not x[0].day1:
#                 d["day1"]=False
#             if not x[0].day2:
#                 d["day2"]=False
#             if not x[0].day3:
#                 d["day3"]=False
#             x = PremimumTicket.objects.filter(email=email)
#             for i in x:
#                 if i.day==1:
#                     d["day1"]=False
#                 elif i.day==2:
#                     d["day2"]=False
#                 elif i.day==3:
#                     d["day3"]=False
            
#             if not d["day1"] and not d["day2"] and not d["day3"]:
#                 d["message"]="You already bought ticket premium ticket for the mainevents you registered"
#                 d["show"]=False
#             return render(request, "premium.html", d)
#         else:
#             d["message"]="You don't have ticket for events"
#             d["show"]=False
#             return render(request, "premium.html", d)
#     except Exception as e:
#         print(traceback.exc())
#         return HttpResponse("<h1>Unexpected Error</h1>")
    

def payment(request):
    try:
        payment_id=request.GET.get("payment_id")
        payment_status = request.GET.get("payment_status")
        payment_request_id = request.GET.get("payment_request_id")
        if not payment_id or not  payment_status or  not payment_request_id:
            return HttpResponse("<h1>Invalid Request</h1>")
        data=instamojo_api.payment_details(payment_request_id, payment_id)
        if Transaction.objects.filter(payment_id=payment_id, payment_request_id=payment_request_id):
            return redirect("test")
        # print(data)
        print(data["payment_request"]["email"], data["payment_request"]["status"], data['payment_request']['purpose'])
        purpose=data['payment_request']['purpose']
        email=data["payment_request"]["email"]
        status=data["payment_request"]["status"]
        amount=data["payment_request"]["amount"]
        if status!="Completed":
            return HttpResponse("<h1>Payment Not Completed Yet</h1>")
        Transaction.objects.create(payment_id=payment_id, payment_request_id=payment_request_id, payment_status=payment_status, 
                                   email=email, status=status, purpose=purpose, amount=int(float(amount)))
        if purpose[:3]=="Day":
            print("Day")
            x=MainEvent.objects.filter(email=email)
            day = purpose[4]
            if x:
                m = MainEvent.objects.get(email=email)
                if day=='1':
                    m.day1=True
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    data = email+f"day{day}"+get_random_string(length=8)
                    qr.add_data(data)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    path = r"static/tickets/"+data+".png"
                    img.save(path)
                    img2 = Image.open(path)
                    new_image = img2.resize((274, 272))
                    new_image.save(path)
                    path_ticket = r"static/main_ticket/"+data+".png"
                    img1 = Image.open(r"static/ticket_template/day1_standard.png")
                    img2 = Image.open(path)
                    img1.paste(img2, (80, 160), mask=img2)
                    img1.save(path_ticket)
                    send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day))
                    m.day1Image=path
                elif day=='2':
                    m.day2=True
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    data = email+f"day{day}"+get_random_string(length=8)
                    qr.add_data(data)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    path = r"static/tickets/"+data+".png"
                    img.save(path)
                    img2 = Image.open(path)
                    new_image = img2.resize((274, 272))
                    new_image.save(path)
                    path_ticket = r"static/main_ticket/"+data+".png"
                    img1 = Image.open(r"static/ticket_template/day2_standard.png")
                    img2 = Image.open(path)
                    img1.paste(img2, (80, 160), mask=img2)
                    img1.save(path_ticket)
                    send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day))
                    m.day2Image=path
                # elif day=='3':
                #     m.day3=True
                #     qr = qrcode.QRCode(version=1, box_size=10, border=5)
                #     data = email+f"day{day}"+get_random_string(length=8)
                #     qr.add_data(data)
                #     qr.make(fit=True)
                #     img = qr.make_image(fill_color="black", back_color="white")
                #     path = r"static/tickets/"+data+".png"
                #     img.save(path)
                #     img2 = Image.open(path)
                #     new_image = img2.resize((274, 272))
                #     new_image.save(path)
                #     path_ticket = r"static/main_ticket/"+data+".png"
                #     img1 = Image.open(r"static/ticket_template/day3_standard.png")
                #     img2 = Image.open(path)
                #     img1.paste(img2, (80, 160), mask=img2)
                #     img1.save(path_ticket)
                #     send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day))
                #     m.day3Image=path
                
                m.save()
            else:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                data = email+f"day{day}"+get_random_string(length=8)
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                path = r"static/tickets/"+data+".png"
                img.save(path)
                img2 = Image.open(path)
                new_image = img2.resize((274, 272))
                new_image.save(path)
                path_ticket = r"static/main_ticket/"+data+".png"
                img1 = Image.open(r"static/ticket_template/day"+str(day)+"_standard.png")
                img2 = Image.open(path)
                img1.paste(img2, (80, 160), mask=img2)
                img1.save(path_ticket)
                send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day))
                if day=='1':
                    m=MainEvent(email=email, day1=True, day1Image=path)
                elif day=='2':
                    m=MainEvent(email=email, day2=True, day2Image=path)
                elif day=='3':
                    m=MainEvent(email=email, day3=True, day3Image=path)
                m.save()
        # elif purpose[:5]=="Combo":
        #     print("Combo")
        #     x=MainEvent.objects.filter(email=email)
        #     print(x)
        #     if x:
        #         m = MainEvent.objects.get(email=email)
        #         m.day1=True
        #         m.day2=True
        #         m.day3=True
        #         m.combo=True
        #         qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #         data = email+"day1"+get_random_string(length=8)
        #         qr.add_data(data)
        #         qr.make(fit=True)
        #         img = qr.make_image(fill_color="black", back_color="white")
        #         path1 = r"static/tickets/"+data+".png"
        #         img.save(path1)
        #         img2 = Image.open(path1)
        #         new_image = img2.resize((274, 272))
        #         new_image.save(path1)
        #         path_ticket1 = r"static/main_ticket/"+data+".png"
        #         img1 = Image.open(r"static/ticket_template/day1_standard.png")
        #         img2 = Image.open(path1)
        #         img1.paste(img2, (80, 160), mask=img2)
        #         img1.save(path_ticket1)
        #         send_mail_func(email=email, path=path1,path_ticket=path_ticket1, day=1)

        #         qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #         data = email+"day2"+get_random_string(length=8)
        #         qr.add_data(data)
        #         qr.make(fit=True)
        #         img = qr.make_image(fill_color="black", back_color="white")
        #         path2 = r"static/tickets/"+data+".png"
        #         img.save(path2)
        #         img2 = Image.open(path2)
        #         new_image = img2.resize((274, 272))
        #         new_image.save(path2)
        #         path_ticket2 = r"static/main_ticket/"+data+".png"
        #         img1 = Image.open(r"static/ticket_template/day2_standard.png")
        #         img2 = Image.open(path2)
        #         img1.paste(img2, (80, 160), mask=img2)
        #         img1.save(path_ticket2)
        #         send_mail_func(email=email, path=path2,path_ticket=path_ticket2, day=2)

        #         qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #         data = email+"day3"+get_random_string(length=8)
        #         qr.add_data(data)
        #         qr.make(fit=True)
        #         img = qr.make_image(fill_color="black", back_color="white")
        #         path3 = r"static/tickets/"+data+".png"
        #         img.save(path3)
        #         img2 = Image.open(path3)
        #         new_image = img2.resize((274, 272))
        #         new_image.save(path3)
        #         path_ticket3 = r"static/main_ticket/"+data+".png"
        #         img1 = Image.open(r"static/ticket_template/day3_standard.png")
        #         img2 = Image.open(path3)
        #         img1.paste(img2, (80, 160), mask=img2)
        #         img1.save(path_ticket3)
        #         send_mail_func(email=email, path=path3,path_ticket=path_ticket3, day=3)
        #         m.day1Image=path1
        #         m.day2Image=path2
        #         m.day3Image=path3
        #         m.save()
        #     else:
        #         # print("Here")
        #         qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #         data = email+"day1"+get_random_string(length=8)
        #         qr.add_data(data)
        #         qr.make(fit=True)
        #         img = qr.make_image(fill_color="black", back_color="white")
        #         path1 = r"static/tickets/"+data+".png"
        #         img.save(path1)
        #         # print("Some error")
        #         img2 = Image.open(path1)
        #         # print("Some error")
        #         new_image = img2.resize((274, 272))
        #         new_image.save(path1)
        #         # print("Some error")
        #         path_ticket1 = r"static/main_ticket/"+data+".png"
        #         img1 = Image.open(r"static/ticket_template/day1_standard.png")
        #         # print("Some error")
        #         img2 = Image.open(path1)
        #         # print("Some error")
        #         img1.paste(img2, (80, 160), mask=img2)
        #         # print("Some error")
        #         img1.save(path_ticket1)
        #         # print("Some error")
        #         send_mail_func(email=email, path=path1,path_ticket=path_ticket1, day=1)

        #         qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #         data = email+"day2"+get_random_string(length=8)
        #         qr.add_data(data)
        #         qr.make(fit=True)
        #         img = qr.make_image(fill_color="black", back_color="white")
        #         path2 = r"static/tickets/"+data+".png"
        #         img.save(path2)
        #         img2 = Image.open(path2)
        #         new_image = img2.resize((274, 272))
        #         new_image.save(path2)
        #         path_ticket2 = r"static/main_ticket/"+data+".png"
        #         img1 = Image.open(r"static/ticket_template/day2_standard.png")
        #         img2 = Image.open(path2)
        #         img1.paste(img2, (80, 160), mask=img2)
        #         img1.save(path_ticket2)
        #         send_mail_func(email=email, path=path2,path_ticket=path_ticket2, day=2)

        #         qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #         data = email+"day3"+get_random_string(length=8)
        #         qr.add_data(data)
        #         qr.make(fit=True)
        #         img = qr.make_image(fill_color="black", back_color="white")
        #         path3 = r"static/tickets/"+data+".png"
        #         img.save(path3)
        #         img2 = Image.open(path3)
        #         new_image = img2.resize((274, 272))
        #         new_image.save(path3)
        #         path_ticket3 = r"static/main_ticket/"+data+".png"
        #         img1 = Image.open(r"static/ticket_template/day3_standard.png")
        #         img2 = Image.open(path3)
        #         img1.paste(img2, (80, 160), mask=img2)
        #         img1.save(path_ticket3)
        #         send_mail_func(email=email, path=path3,path_ticket=path_ticket3, day=3)
        #         m=MainEvent(email=email, day1=True, day2=True, day3=True, day1Image=path1, day2Image=path2, day3Image=path3, combo=True)
        #         m.save()
        # elif purpose[:12]=="Fanpit Combo":
        #     print("Fanpit Combo")
        #     qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #     data = email+"premiumday1"+get_random_string(length=8)
        #     qr.add_data(data)
        #     qr.make(fit=True)
        #     img = qr.make_image(fill_color="black", back_color="white")
        #     path1 = r"static/tickets/"+data+".png"
        #     img.save(path1)
        #     img2 = Image.open(path1)
        #     new_image = img2.resize((274, 272))
        #     new_image.save(path1)
        #     path_ticket1 = r"static/main_ticket/"+data+".png"
        #     img1 = Image.open(r"static/ticket_template/day1_premium.png")
        #     img2 = Image.open(path1)
        #     img1.paste(img2, (80, 160), mask=img2)
        #     img1.save(path_ticket1)
        #     send_mail_func(email=email, path=path1,path_ticket=path_ticket1, day=1, t=True)

        #     qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #     data = email+"premiumday2"+get_random_string(length=8)
        #     qr.add_data(data)
        #     qr.make(fit=True)
        #     img = qr.make_image(fill_color="black", back_color="white")
        #     path2 = r"static/tickets/"+data+".png"
        #     img.save(path2)
        #     img2 = Image.open(path2)
        #     new_image = img2.resize((274, 272))
        #     new_image.save(path2)
        #     path_ticket2 = r"static/main_ticket/"+data+".png"
        #     img1 = Image.open(r"static/ticket_template/day2_premium.png")
        #     img2 = Image.open(path2)
        #     img1.paste(img2, (80, 160), mask=img2)
        #     img1.save(path_ticket2)
        #     send_mail_func(email=email, path=path2,path_ticket=path_ticket2, day=2, t=True)

        #     qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #     data = email+"premiumday3"+get_random_string(length=8)
        #     qr.add_data(data)
        #     qr.make(fit=True)
        #     img = qr.make_image(fill_color="black", back_color="white")
        #     path3 = r"static/tickets/"+data+".png"
        #     img.save(path3)
        #     img2 = Image.open(path3)
        #     new_image = img2.resize((274, 272))
        #     new_image.save(path3)
        #     path_ticket3 = r"static/main_ticket/"+data+".png"
        #     img1 = Image.open(r"static/ticket_template/day3_premium.png")
        #     img2 = Image.open(path3)
        #     img1.paste(img2, (80, 160), mask=img2)
        #     img1.save(path_ticket3)
        #     send_mail_func(email=email, path=path3,path_ticket=path_ticket3, day=3, t=True)
        #     m=MainEvent(email=email, day1=True, day2=True, day3=True, day1Image=path1, day2Image=path2, day3Image=path3, combo=True, 
        #                 premium1=True, premium2=True, premium3=True)
        #     m.save()
        # elif purpose[:6]=="Fanpit":
        #     print("Fanpit")
        #     x=MainEvent.objects.filter(email=email)
        #     day=purpose.split()[2]
        #     if "REC" in purpose:
        #         if x:
        #             m = MainEvent.objects.get(email=email)
        #             d1=m.day1
        #             d2=m.day2
        #             d3=m.day3
        #             if day=='1':
        #                 m.premium1=True
        #                 d1=True
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"premiumday{day}"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day1_premium.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day), t=True)
        #                 m.day1Image=path
        #             elif day=='2':
        #                 m.premium2=True
        #                 d2=True
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"premiumday{day}"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day2_premium.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day), t=True)
        #                 m.day2Image=path
        #             elif day=='3':
        #                 m.premium3=True
        #                 d3=True
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"premiumday{day}"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day3_premium.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day), t=True)
        #                 m.day3Image=path
                    
        #             if not d1:
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day1"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day1_standard.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=1)
        #                 m.day1Image=path
        #             if not d2:
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day2"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day2_standard.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=2)
        #                 m.day2Image=path
        #             if not d3:
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day3"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day3_standard.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=3)
        #                 m.day3Image=path
        #             m.day1=True
        #             m.day2=True
        #             m.day3=True
        #             m.save()
        #         else:
        #             qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #             data = email+f"premiumday{day}"+get_random_string(length=8)
        #             qr.add_data(data)
        #             qr.make(fit=True)
        #             img = qr.make_image(fill_color="black", back_color="white")
        #             path = r"static/tickets/"+data+".png"
        #             img.save(path)
        #             img2 = Image.open(path)
        #             new_image = img2.resize((274, 272))
        #             new_image.save(path)
        #             path_ticket = r"static/main_ticket/"+data+".png"
        #             img1 = Image.open(r"static/ticket_template/day"+str(day)+"_premium.png")
        #             img2 = Image.open(path)
        #             img1.paste(img2, (80, 160), mask=img2)
        #             img1.save(path_ticket)
        #             send_mail_func(email=email, path=path, path_ticket=path_ticket,day=int(day), t=True)

        #             if day=='1':
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day2"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path2 = r"static/tickets/"+data+".png"
        #                 img.save(path2)
        #                 img2 = Image.open(path2)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path2)
        #                 path_ticket2 = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day2_standard.png")
        #                 img2 = Image.open(path2)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket2)
        #                 send_mail_func(email=email, path=path2,path_ticket=path_ticket2, day=2)


        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day3"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path3 = r"static/tickets/"+data+".png"
        #                 img.save(path3)
        #                 img2 = Image.open(path3)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path3)
        #                 path_ticket3 = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day3_standard.png")
        #                 img2 = Image.open(path3)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket3)
        #                 send_mail_func(email=email, path=path3,path_ticket=path_ticket3, day=3)
        #                 m=MainEvent(email=email, day1=True, day2=True, day3=True,day1Image=path,day2Image=path2, day3Image=path3, premium1=True)
        #             elif day=='2':
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day1"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path1 = r"static/tickets/"+data+".png"
        #                 img.save(path1)
        #                 img2 = Image.open(path1)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path1)
        #                 path_ticket1 = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day1_standard.png")
        #                 img2 = Image.open(path1)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket1)
        #                 send_mail_func(email=email, path=path1,path_ticket=path1, day=1)


        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day3"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path3 = r"static/tickets/"+data+".png"
        #                 img.save(path3)
        #                 img2 = Image.open(path3)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path3)
        #                 path_ticket3 = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day3_standard.png")
        #                 img2 = Image.open(path3)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket3)
        #                 send_mail_func(email=email, path=path3,path_ticket=path_ticket3, day=3)
        #                 m=MainEvent(email=email, day1=True,day2=True, day3=True, day2Image=path,day1Image=path1, day3Image=path3, premium2=True)
        #             elif day=='3':
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day1"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path1 = r"static/tickets/"+data+".png"
        #                 img.save(path1)
        #                 img2 = Image.open(path1)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path1)
        #                 path_ticket1 = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day1_standard.png")
        #                 img2 = Image.open(path1)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket1)
        #                 send_mail_func(email=email, path=path1,path_ticket=path1, day=1)


        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"day2"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path2 = r"static/tickets/"+data+".png"
        #                 img.save(path2)
        #                 img2 = Image.open(path2)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path2)
        #                 path_ticket2 = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day2_standard.png")
        #                 img2 = Image.open(path2)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket2)
        #                 send_mail_func(email=email, path=path2,path_ticket=path_ticket2, day=2)
        #                 m=MainEvent(email=email, day1=True,day2=True, day3=True, day3Image=path, day2Image=path2,day1Image=path1,premium3=True)
        #             m.save()
        #     else:
        #         if x:
        #             m = MainEvent.objects.get(email=email)
        #             if day=='1':
        #                 m.day1=True
        #                 m.premium1=True
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"premiumday{day}"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day1_premium.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day), t=True)
        #                 m.day1Image=path
        #                 m.save()
        #             elif day=='2':
        #                 m.day2=True
        #                 m.premium2=True
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"premiumday{day}"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day2_premium.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day), t=True)
        #                 m.day2Image=path
        #                 m.save()
        #             elif day=='3':
        #                 m.day3=True
        #                 m.premium3=True
        #                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #                 data = email+f"premiumday{day}"+get_random_string(length=8)
        #                 qr.add_data(data)
        #                 qr.make(fit=True)
        #                 img = qr.make_image(fill_color="black", back_color="white")
        #                 path = r"static/tickets/"+data+".png"
        #                 img.save(path)
        #                 img2 = Image.open(path)
        #                 new_image = img2.resize((274, 272))
        #                 new_image.save(path)
        #                 path_ticket = r"static/main_ticket/"+data+".png"
        #                 img1 = Image.open(r"static/ticket_template/day3_premium.png")
        #                 img2 = Image.open(path)
        #                 img1.paste(img2, (80, 160), mask=img2)
        #                 img1.save(path_ticket)
        #                 send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day), t=True)
        #                 m.day3Image=path
        #                 m.save()
                    
        #         else:
        #             qr = qrcode.QRCode(version=1, box_size=10, border=5)
        #             data = email+f"premiumday{day}"+get_random_string(length=8)
        #             qr.add_data(data)
        #             qr.make(fit=True)
        #             img = qr.make_image(fill_color="black", back_color="white")
        #             path = r"static/tickets/"+data+".png"
        #             img.save(path)
        #             img2 = Image.open(path)
        #             new_image = img2.resize((274, 272))
        #             new_image.save(path)
        #             path_ticket = r"static/main_ticket/"+data+".png"
        #             img1 = Image.open(r"static/ticket_template/day"+str(day)+r"_premium.png")
        #             img2 = Image.open(path)
        #             img1.paste(img2, (80, 160), mask=img2)
        #             img1.save(path_ticket)
        #             send_mail_func(email=email, path=path,path_ticket=path_ticket, day=int(day), t=True)
        #             if day=='1':
        #                 m=MainEvent(email=email, day1=True, day1Image=path, premium1=True)
        #             elif day=='2':
        #                 m=MainEvent(email=email, day2=True, day2Image=path, premium2=True)
        #             elif day=='3':
        #                 m=MainEvent(email=email, day3=True, day3Image=path, premium3=True)
        #             m.save()
        elif purpose[:5]=="Event":
            print("Event")
            id = purpose.split()[1]
            e=EventRegister.objects.get(email=email, event_id=id)
            e.paid=True
            event_register_id=e.id
            e.save()
            temp=TeamMates.objects.filter(event_register_id=event_register_id)
            if temp:
                temp.update(verified=True)
            print(id)
            z=Event.objects.get(id=int(id))
            z.registrations = int(z.registrations)+1
            z.save()
        elif "Merch" in purpose:
            print(purpose)
            size = purpose.split()[-1]
            print(size)
            Merch.objects.create(email=email, size=size)
            
        print("Exited")
        return redirect("test")
    except Exception as e:
        print(traceback.exc())
        return HttpResponse("<h1>Invalid Request</h1>")
    
    

# http://localhost:8000/test?payment_id=MOJO3302E05Q52340490&payment_status=Credit&payment_request_id=d693d35d51cc4f59820f290f8991fccb
def payment1(request):
    x=request.GET["payment_id"]
    instamojo_api.payment_details1(x)
    return HttpResponse("Message")

def merch(request):
    try:
        token = request.COOKIES.get('jwt')
        if not token:
            print(token)
            return redirect("login")
        
        try:
            payload = jwt.decode(token, 'gahih1h26*&&^@^*GHhduhau^&^*782hgh*&^&^&ghdghay^&^&^*&ghdghag87^&^&ghdsa876738gh78t78GYUT^6736gyd6756^&TYGT6738827y7gh*&&^%^&&^%&*hhdyiasudhikhsakhGHGHDGHSGKGKHgyudgyushjhgjGDhGSHDg*^%*^^&^&now_you_decode_ra', 'HS256')
        except jwt.ExpiredSignatureError as e:
            print(traceback.exc())
            return redirect("login")
        email=payload['id']
        m={}
        m["s"] = len(Merch.objects.filter(size="S").values())<70
        m["m"] = len(Merch.objects.filter(size="M").values())<170
        m["l"] = len(Merch.objects.filter(size="L").values())<170
        m["xl"] = len(Merch.objects.filter(size="XL").values())<60
        m["message"]=""
        if request.method=="POST":
            size = request.POST.get("day")
            if not size or size not in ["S", "M", "L", "XL"]:
                m["message"]="Please select a size for your T-Shirt"
                return render(request, "merch.html", m)
            amount = 365
            # amount = 10
            purpose = f'Recharge Merch T-shirt {size}'

            # payment_url = instamojo_api.create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url)
            payment_url = instamojo_api.payment_request(email, amount, purpose)
            if payment_url is None:
                return HttpResponse("<h1>Not able to load payment url. Sorry for the inconvenience</h1>")
            return redirect(payment_url)
        
        return render(request, "merch.html", m)
    except Exception as e:
        print(traceback.exc())
        return HttpResponse("<h1>Unexpected Error</h1>")
