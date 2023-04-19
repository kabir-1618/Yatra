from django.urls import path
from . import views

urlpatterns=[
    path("register", views.register,name='register'),
    path('login', views.login, name='login'),
    path("", views.test, name='test'),
    path("mainevent", views.mainevent, name="mainevent"),
    path("verify_email", views.verify_email, name="verify_email"),
    path("resendmail", views.resendmail, name="resendmail"),
    path("merch",views.merch),
    path("forgotpassword", views.forgotpassword, name="forgotpassword"),
    path("forgot_password_verification", views.forgot_password_verification, name="forgot_password_verification"),
    path("payment", views.payment, name="payment"),
    path("logout", views.logout, name='logout'),
    path("events/<id>", views.event, name="event"),
]

# path("premiumticket", views.premiumticket, name="premiumticket"),
